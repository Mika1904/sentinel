# Data Sources and Notes

All data in this project comes from the **Wellcome Sanger Institute** ([GDSC](https://www.cancerrxgene.org/) and [Cell Model Passports](https://cellmodelpassports.sanger.ac.uk/downloads)). It covers cancer cell lines grown in the lab and contains no patient records.

## Files used in `Sentinel.ipynb`

| File | What it contains | Download URL |
|---|---|---|
| `GDSC2_fitted_dose_response_27Oct23.xlsx` | Drug response (`LN_IC50`), drug ID, drug name and putative target for 242,036 cell line x drug experiments | `https://cmp.cog.sanger.ac.uk/download/GDSC2_fitted_dose_response_27Oct23.xlsx` |
| `model_list_20261013.csv` | Cell line metadata (`model_id`, tissue, cancer type, patient sex and age at sampling) | `https://cog.sanger.ac.uk/cmp/download/model_list_20261013.csv` |
| `mutations_summary_20260724.zip` | Driver gene mutations per sequenced cell line | `https://cog.sanger.ac.uk/cmp/download/mutations_summary_20260724.zip` |
| `model_dataset_availability_20260727.csv` | Records which cell lines have whole-exome or whole-genome sequencing | `https://cog.sanger.ac.uk/cmp/download/model_dataset_availability_20260727.csv` |

## Data notes and cleaning steps

1. **Sequenced cell lines only.** A cell line missing from the mutation table might simply not have been sequenced. We check `model_dataset_availability_20260727.csv` first and keep the 965 sequenced cell lines.
2. **Non-cancer cell lines.** 7 sequenced lines are marked `Non-Cancerous` in `model_list_20261013.csv` and are removed before modelling, leaving 958 cancer cell lines and 239,081 drug-response rows.
3. **Drug IDs vs drug names.** 9 drug names were screened under two different `DRUG_ID` values, so we group and model by `DRUG_ID` (295 drugs).
4. **Excluded genes with repeated identical variants.** For 6 genes (`SDHA`, `CBLC`, `POLQ`, `KMT2C`, `HLA-A`, `HLA-B`), most listed mutations are the exact same DNA/protein change across unrelated cell lines (likely germline variants or sequencing artefacts). We leave these 6 genes out and keep the remaining 84 genes mutated in at least 20 cell lines.
5. **Dose ranges.** Each drug was tested over its own concentration range, and in 71.8% of rows the fitted `IC50` is above the highest concentration tested. Raw `ln(IC50)` values are therefore always compared against that drug's own training average.

## Usage policy

Under the [Sanger DepMap Data Usage Policy](https://depmap.sanger.ac.uk/documentation/data-usage-policy/), the data is free to use for academic and educational research but should not be redistributed. For that reason, raw files are not committed to this repository; `Sentinel.ipynb` downloads them directly from Sanger when run.

## Citations and tools

**Data citations:**
1. Yang W, Soares J, Greninger P, et al. Genomics of Drug Sensitivity in Cancer (GDSC): a resource for therapeutic biomarker discovery in cancer cells. *Nucleic Acids Research*. 2013;41(D1):D955-D961. https://doi.org/10.1093/nar/gks1111
2. Iorio F, Knijnenburg TA, Vis DJ, et al. A Landscape of Pharmacogenomic Interactions in Cancer. *Cell*. 2016;166(3):740-754. https://doi.org/10.1016/j.cell.2016.06.017
3. van der Meer D, Barthorpe S, Yang W, et al. Cell Model Passports — a hub for clinical, genetic and functional datasets of preclinical cancer models. *Nucleic Acids Research*. 2019;47(D1):D923-D929. https://doi.org/10.1093/nar/gky872

**Software & tools:**
Python, pandas, NumPy, Matplotlib, Seaborn, scikit-learn, LightGBM, Gradio, Google Colab. Coding assistants (Claude / Gemini) were used to help find Sanger download URLs, check data merges and structure the notebook.
