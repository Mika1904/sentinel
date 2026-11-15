<p align="center">
  <img src="Project_Code/figures/Sentinel_Logo.png" width="180" alt="Team Sentinel Logo">
</p>

# Sentinel

**Which cancer drugs should a lab test first?**
AI + Health track · Veritas AI International High School Hackathon 2026

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Mika1904/sentinel/blob/main/Project_Code/Team_Sentinel_Health_AI.ipynb)

*This project is a prototype and is not medical advice. All data comes from cancer cell lines grown in a laboratory, not from patients.*

## What it does
Sentinel is for a cancer researcher who has a new cancer cell line and only enough time and budget to test a few drugs on it. They enter the cell line's tissue type and mutated genes, and Sentinel ranks all 295 screened drugs by how likely the cell line is to respond, with a confidence level for each drug and the genes that move each prediction most.

Running the most promising experiments first gives faster answers about which mutations make tumours respond to which drugs, the knowledge doctors later use to match treatments to a patient's tumour. Sentinel does not make treatment decisions and has not been tested on patient samples.

<p align="center">
  <img src="Project_Code/figures/plot11_drug_shortlist.png" width="600" alt="Drug shortlist for the held-out cell line SK-MEL-3">
</p>

For SK-MEL-3, a melanoma cell line the model never saw, the top two drugs are the BRAF inhibitors PLX-4720 and Dabrafenib, and both were sensitive in the lab.

## Results
All results are on 192 cell lines held out from training (47,468 drug results). Knowing the drug alone already gives R² = 0.716, so we compare methods by **within-drug R²**: how much of the difference between cell lines on the same drug each method explains.

| Method | RMSE | Within-drug R² |
|---|---|---|
| Per-drug average | 1.464 | -0.007 |
| Per-drug + tissue average | 1.324 | 0.177 |
| Linear regression | 1.403 | 0.076 |
| First LightGBM | 1.339 | 0.159 |
| **Final model** (50/50 blend of the tissue average and a drug-centred LightGBM) | **1.302** | **0.204** |

- **Shortlist:** 44.3% of the drugs in Sentinel's top 10 were truly sensitive, against 41.6% for the per-drug + tissue average and 20.3% for random drugs.
- **Missed cases and false alarms:** the final model finds 2,800 of 9,634 sensitive results (29.1%) and misses 6,834, with 1,476 false alarms (3.9%).
- **How solid the gain is:** the final model beats the per-drug + tissue average on all 10 extra random splits, but only by 0.016 within-drug R² on average.
- **Where it fails:** solid tumours (within-drug R² 0.077 for lung against 0.554 for blood cancers), tissues with very few cell lines, and rare mutations such as EGFR.

The notebook also checks results across sex and age groups and shows what the mutation features add.

## Repository layout
| Path | Contents |
|---|---|
| `Project_Code/Team_Sentinel_Health_AI.ipynb` | The whole project: data, baselines, final model, evaluation, drug shortlist and the Sentinel web app |
| `Project_Code/figures/` | Saved plots |
| `Project_Code/data/DATA_SOURCES.md` | Where the data comes from, usage terms and citations |

## How to run
Open the notebook in Google Colab (button above) and choose **Runtime → Run all**. Section 21 starts the Sentinel web app and prints a link to open it. The notebook downloads the public data from the Wellcome Sanger Institute automatically; no uploads or API keys are needed.

## Data and sources
GDSC2 drug-response data and Cell Model Passports annotations, Wellcome Sanger Institute. Raw data is not stored in this repository (see `Project_Code/data/DATA_SOURCES.md` for sources, licence and citations). Software, papers and AI tools used are listed in Section 23 of the notebook.
