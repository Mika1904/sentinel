<p align="center">
  <img src="Project_Code/figures/sentinel_logo.png" width="180" alt="Team Sentinel Logo">
</p>

# Sentinel

**Explainable drug-response prediction from tumor genomics**
AI + Health track · Veritas AI International High School Hackathon 2026

*This project is a prototype and is not medical advice. All data comes from cancer cell lines grown in a laboratory, not from patients.*

## What it does
Sentinel takes a cancer cell line's tissue type and mutations and predicts how sensitive it is to a panel of cancer drugs (ln IC50). The project compares the model against simple baselines, reports where it fails, and shows "what-if" explanations of which mutations drive a prediction.

**Current status:** data download, exploration, cell-line split, baselines and first LightGBM model are complete in `Project_Code/Sentinel.ipynb`. Model improvement, failure analysis, what-if toggles and demo are in progress.

## Repository layout
| Path | Contents |
|---|---|
| `Project_Code/Sentinel.ipynb` | Data download, exploration, cell-line split, baselines and first LightGBM model |
| `Project_Code/figures/` | Saved plots |
| `Project_Code/data/DATA_SOURCES.md` | Where the data comes from, usage terms and citations |

## How to run
Open `Project_Code/Sentinel.ipynb` in Google Colab and choose **Runtime → Run all** (about 1–2 minutes). The notebook downloads the public data from the Wellcome Sanger Institute automatically; no uploads or API keys are needed.

## Data
GDSC2 drug-response data and Cell Model Passports annotations, Wellcome Sanger Institute. Raw data is not stored in this repository (see `Project_Code/data/DATA_SOURCES.md` for sources, licence and citations).
