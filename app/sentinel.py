"""Sentinel: which cancer drugs should a lab test first?

Hosted version of the app in Section 29 of Project_Code/Team_Sentinel_Health_AI.ipynb.
It loads the fitted final model saved by the notebook (model_bundle.joblib) and uses the
same prediction steps. No raw data is included. Research prototype, not medical advice.
"""
import os

import gradio as gr
import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

B = joblib.load(os.path.join(os.path.dirname(__file__), "model_bundle.joblib"))
GENES, DRUGS, TISSUES = B["GENES"], B["DRUGS"], B["TISSUES"]
drug_info, confidence, flag_cutoff, FLAG_LEVEL = B["drug_info"], B["confidence"], B["flag_cutoff"], B["FLAG_LEVEL"]
expr_fit = B["expr_fit"]
EXPR_COLS = expr_fit["pc_cols"] + ["has_expression"]


# ---------- prediction (same steps as the notebook's final model) ----------
def make_profile(tissue, mutated_genes, drug_ids):
    profile = pd.DataFrame({"DRUG_ID": drug_ids, "tissue": tissue})
    for gene in GENES:
        profile[gene] = int(gene in mutated_genes)
    return profile


def expression_rows(rows, example_name=None):
    # a held-out example line uses its own RNA-seq features; anything else uses its tissue's average
    if example_name is not None:
        vector = B["examples"][example_name]["expr"]
    else:
        tissue = rows["tissue"].iloc[0]
        means = expr_fit["tissue_means"]
        mean = means.loc[tissue].values if tissue in means.index else expr_fit["global_mean"].values
        vector = np.append(mean, 0.0)
    return pd.DataFrame(np.tile(vector, (len(rows), 1)), index=rows.index, columns=EXPR_COLS)


def drug_tissue_average(rows):
    base = rows["DRUG_ID"].map(B["drug_avg"]).values
    pred = rows.set_index(["DRUG_ID", "tissue"]).index.map(B["drug_tissue_avg"]).to_numpy(dtype=float)
    return np.where(np.isnan(pred), base, pred)


def lgbm_features(rows, ex_rows):
    X = rows[["DRUG_ID", "tissue"] + GENES].copy()
    for col, categories in B["lgb_categories"].items():
        X[col] = pd.Categorical(X[col].where(X[col].isin(categories)), categories=categories)
    return pd.concat([X, ex_rows], axis=1)


def ridge_inputs(rows, tissues):
    tissue_columns = np.column_stack([rows["tissue"].values == t for t in tissues]).astype(float)
    return np.hstack([tissue_columns, rows[GENES].values.astype(float)])


def two_stage_ridge(rows, ex_rows):
    mutation_part = B["ridges"]["mut"]
    X = ridge_inputs(rows, mutation_part["tissues"])
    pred = np.zeros(len(rows))
    for drug_id, ridge in mutation_part["ridges"].items():
        mask = rows["DRUG_ID"].values == drug_id
        if mask.any():
            pred[mask] = ridge.predict(X[mask])
    for drug_id, ridge in B["ridges"]["expr"].items():
        mask = rows["DRUG_ID"].values == drug_id
        if mask.any():
            pred[mask] += ridge.predict(ex_rows.values[mask])
    return pred


def predict(rows, example_name=None):
    ex_rows = expression_rows(rows, example_name)
    p_tissue = drug_tissue_average(rows)
    p_centered = rows["DRUG_ID"].map(B["drug_avg"]).values + B["centered"].predict(lgbm_features(rows, ex_rows))
    p_ridge = two_stage_ridge(rows, ex_rows)
    weights = B["drug_weights"]
    if weights is None:
        return (p_tissue + p_centered + p_ridge) / 3
    w = rows["DRUG_ID"].map(weights).fillna(1 / 3).values
    return (1 - w) / 2 * (p_tissue + p_centered) + w * p_ridge


def works_at_dose(drug_ids, preds):
    # predicted IC50 below the drug's highest tested concentration
    return np.asarray(preds) < np.log(pd.Series(drug_ids).map(B["drug_max_conc"]).values)


def drug_percentile(drug_ids, preds):
    levels = B["percentile_levels"]
    return np.array([np.interp(p, B["percentile_values"][d], levels) for d, p in zip(drug_ids, preds)])


# ---------- shortlist, gene effects and warnings (same as the notebook) ----------
def rank_drugs(pred, top=10):
    works = works_at_dose(DRUGS, pred)
    table = pd.DataFrame({
        "DRUG_ID": DRUGS,
        "name": drug_info.loc[DRUGS, "DRUG_NAME"].values,
        "Drug": drug_info.loc[DRUGS, "label"].values,
        "Target": drug_info.loc[DRUGS, "PUTATIVE_TARGET"].values,
        "Percentile": drug_percentile(DRUGS, pred),
        "Predicted sensitive": np.where(pred <= flag_cutoff.reindex(DRUGS).values, "Yes", "No"),
        "Works at tested dose": np.where(works, "Yes", "No"),
        "Confidence": confidence.reindex(DRUGS).values,
    })
    if B["POTENCY_PASS"]:
        table = table.sort_values(["Works at tested dose", "Percentile"], ascending=[False, True], kind="stable")
    else:
        table = table.sort_values("Percentile", kind="stable")
    table = table.drop_duplicates("name").drop(columns="name")
    table = table.head(top).reset_index(drop=True)
    table["Percentile"] = table["Percentile"].round().astype(int)
    table.insert(0, "Rank", range(1, len(table) + 1))
    return table


def shortlist(tissue, mutated_genes, example_name=None, top=10):
    return rank_drugs(predict(make_profile(tissue, mutated_genes, DRUGS), example_name), top)


def gene_effects(tissue, mutated_genes, drug_id, example_name=None, top=5):
    base = make_profile(tissue, mutated_genes, [drug_id])
    flipped = pd.concat([base] * len(GENES), ignore_index=True)
    for i, gene in enumerate(GENES):
        flipped.loc[i, gene] = 1 - flipped.loc[i, gene]
    before = int(round(drug_percentile([drug_id], predict(base, example_name))[0]))
    after = drug_percentile([drug_id] * len(GENES), predict(flipped, example_name)).round().astype(int)
    table = pd.DataFrame({
        "Gene": GENES,
        "Change": ["mutated → not mutated" if g in mutated_genes else "not mutated → mutated" for g in GENES],
        "Percentile after": after,
        "Shift": after - before,
    })
    table = table[table["Shift"] != 0]
    table["Effect"] = np.where(table["Shift"] < 0, "more sensitive", "less sensitive")
    table = table.sort_values("Shift", key=lambda s: s.abs(), ascending=False, kind="stable")
    return table.head(top).reset_index(drop=True)


def short_list(genes, n=5):
    return ", ".join(genes[:n]) + (f" and {len(genes) - n} more" if len(genes) > n else "")


def input_warnings(tissue, mutated_genes, example_name=None):
    notes = []
    n_tissue = int(B["lines_per_tissue"].get(tissue, 0))
    if n_tissue == 0:
        notes.append(f"No training cell lines come from {tissue}, so the model can only use each drug's average and the gene features.")
    elif n_tissue < 10:
        notes.append(f"Only {n_tissue} training cell line(s) come from {tissue}, so this shortlist is unreliable.")
    rare = [g for g in mutated_genes if B["lines_per_gene"][g] < 20]
    if rare:
        notes.append(f"Fewer than 20 training cell lines have a mutation in {short_list(rare)}, so the model has learned little about these mutations.")
    counts = B["tissue_gene_counts"]
    unseen = [g for g in mutated_genes if tissue in counts.index and counts.loc[tissue, g] == 0]
    if unseen and n_tissue > 0:
        notes.append(f"None of the {tissue} cell lines the model learned from has a mutation in {short_list(unseen)}, "
                     "so the model's estimate for these genes here is borrowed from other tissues.")
    if len(mutated_genes) > B["max_genes"]:
        notes.append(f"{len(mutated_genes)} mutated genes is more than any training cell line has ({B['max_genes']}).")
    elif len(mutated_genes) > 10:
        notes.append(f"{len(mutated_genes)} mutated genes is unusual: real cell lines in our data rarely have more than 10 of "
                     "these 84 genes mutated. With many mutations the model tends to call too many drugs sensitive.")
    if example_name is None:
        notes.append(f"No gene expression data was entered, so the app assumes the average expression of {tissue} cell lines. "
                     "Predictions are less precise than for the example cell lines, which use their own RNA-seq data.")
    elif not B["examples"][example_name]["has_rnaseq"]:
        notes.append("RNA-seq expression is missing for this cell line, so the tissue average is used.")
    return notes


def add_lab_result(table, name):
    results = B["lab_results"][name]
    return table.assign(**{"Lab result": [results.get(d, "not tested") for d in table["DRUG_ID"]]})


def plot_shortlist(table, title):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = table["Confidence"].map({"High": "#2b7a4b", "Medium": "#e0a43a", "Low": "#b9c0cc"})
    labels = table["Drug"] + " (" + table["Target"].str.slice(0, 22) + ")"
    ax.barh(labels[::-1], table["Percentile"][::-1], color=colors[::-1])
    ax.set_xlim(0, 100)
    ax.set_xlabel("predicted percentile for the drug (lower = more sensitive)")
    ax.set_title(title)
    for level, color in [("High", "#2b7a4b"), ("Medium", "#e0a43a"), ("Low", "#b9c0cc")]:
        ax.bar(0, 0, color=color, label=f"{level} confidence")
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    return fig


# ---------- the app ----------
TEST_LINES = sorted(B["examples"])
EXAMPLE, NEW_LINE = "Example: held-out cell line", "Enter a new cell line"
LOGO = os.path.join(os.path.dirname(__file__), "..", "Project_Code", "figures", "Sentinel_Logo.png")


def ask_for(text):
    return text, None, None, gr.update(choices=[], value=None), None


def find_drugs(mode, line_name, tissue, genes):
    genes = genes or []
    if mode == EXAMPLE and not line_name:
        return ask_for("Please pick a held-out cell line.")
    if mode == NEW_LINE and not tissue:
        return ask_for("Please pick a tissue.")
    if mode == EXAMPLE:
        tissue, genes = B["examples"][line_name]["tissue"], B["examples"][line_name]["genes"]
        example_name, name = line_name, line_name
    else:
        example_name, name = None, "Your cell line"
    table = shortlist(tissue, genes, example_name)
    if mode == EXAMPLE:
        table = add_lab_result(table, line_name)
    # the flag follows the percentile shown, so the two never disagree at the boundary
    table["Predicted sensitive"] = np.where(table["Percentile"] <= round(100 * FLAG_LEVEL), "Yes", "No")
    summary = f"### {name}\n{tissue} · mutated: {', '.join(genes) if genes else 'none of the 84 genes'}"
    n_flagged = int((table["Predicted sensitive"] == "Yes").sum())
    if n_flagged > 0:
        summary += f"\n\n**{n_flagged} of the top 10** are predicted sensitive (in the lowest {FLAG_LEVEL:.0%} for that drug)."
    else:
        summary += f"\n\n**No drug is predicted sensitive** for this profile (none reaches the lowest {FLAG_LEVEL:.0%}), so treat the list as weak candidates."
    notes = input_warnings(tissue, genes, example_name)
    for note in notes:
        summary += f"\n\n**Caution:** {note}"
    if any(not note.startswith(("No gene expression", "RNA-seq expression is missing")) for note in notes):
        summary += "\n\n**This profile is unusual for the model, so treat the whole list with extra caution.**"
    choices = [(drug, int(drug_id)) for drug, drug_id in zip(table["Drug"], table["DRUG_ID"])]
    profile = {"tissue": tissue, "genes": list(genes), "example": example_name}
    fig = plot_shortlist(table, "Top 10 drugs")
    plt.close(fig)
    shown = table.drop(columns="DRUG_ID").rename(columns={"Confidence": "Drug reliability"})
    return (summary, shown, fig,
            gr.update(choices=choices, value=choices[0][1]), profile)


def why(profile, drug_id):
    if not profile or drug_id is None:
        return None
    return gene_effects(profile["tissue"], profile["genes"], int(drug_id), profile.get("example"))


def switch_mode(mode):
    test_mode = mode == EXAMPLE
    return gr.update(visible=test_mode), gr.update(visible=not test_mode), gr.update(visible=not test_mode)


FONT = gr.themes.GoogleFont("Inter")
THEME = gr.themes.Soft(font=FONT, font_mono=FONT)
CSS = ".gradio-container {width: 100%; max-width: 960px !important; margin: 0 auto !important} #header, #footer {text-align: center}"

with gr.Blocks(title="Sentinel") as app:
    if os.path.exists(LOGO):
        gr.Image(LOGO, show_label=False, container=False, buttons=[], interactive=False, height=110)
    gr.Markdown("# Sentinel\nWhich cancer drugs should a lab test first?", elem_id="header")
    profile_state = gr.State()
    with gr.Column(variant="panel"):
        with gr.Row():
            mode = gr.Radio([EXAMPLE, NEW_LINE], value=EXAMPLE, label="Input")
            line_box = gr.Dropdown(TEST_LINES, value="SK-MEL-3", label="Held-out cell line")
            tissue_box = gr.Dropdown(TISSUES, value="Skin", label="Tissue", visible=False)
            gene_box = gr.Dropdown(GENES, value=["BRAF"], multiselect=True, label="Mutated genes", visible=False)
        find_button = gr.Button("Find drugs", variant="primary")
    summary_box = gr.Markdown()
    with gr.Tabs():
        with gr.Tab("Top 10 drugs"):
            table_box = gr.Dataframe(interactive=False, buttons=[], label="Lower percentile = more sensitive. Works at tested dose = predicted to reach 50% kill below the highest dose tested. Drug reliability = how well each drug was predicted in testing, not how sure the model is about this profile.")
        with gr.Tab("Chart"):
            plot_box = gr.Plot(show_label=False)
        with gr.Tab("Why this drug?"):
            drug_box = gr.Dropdown(label="Pick a drug", choices=[])
            genes_box = gr.Dataframe(interactive=False, buttons=[], label="Genes that move this prediction most (negative shift = more sensitive)")
    gr.Markdown("*Research prototype on lab cell lines, not medical advice. Data: GDSC2 and Cell Model Passports, "
                "Wellcome Sanger Institute.*", elem_id="footer")

    inputs = [mode, line_box, tissue_box, gene_box]
    outputs = [summary_box, table_box, plot_box, drug_box, profile_state]
    mode.change(switch_mode, mode, [line_box, tissue_box, gene_box])
    find_button.click(find_drugs, inputs, outputs).then(why, [profile_state, drug_box], genes_box)
    app.load(find_drugs, inputs, outputs).then(why, [profile_state, drug_box], genes_box)
    drug_box.change(why, [profile_state, drug_box], genes_box)

if __name__ == "__main__":
    # Render sets PORT; locally the app opens on port 7860
    app.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)),
               theme=THEME, css=CSS, footer_links=[])
