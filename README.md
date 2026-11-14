<p align="center">
  <img src="Project_Code/figures/Sentinel_Logo.png" width="180" alt="Team Sentinel Logo">
</p>

# Sentinel

**Explainable drug-response prediction from tumor genomics**
AI + Health track · Veritas AI International High School Hackathon 2026

*This project is a prototype and is not medical advice. All data comes from cancer cell lines grown in a laboratory, not from patients.*

## What it does
Sentinel helps cancer researchers decide which drugs to test first. Given a cell line's tissue type and mutations, it predicts its response (ln IC50) to 295 drug screens, ranks the drugs into a shortlist with a confidence level for each, and shows which mutations drive each prediction. The notebook compares the model with simple baselines on held-out cell lines, reports missed cases and false alarms, checks results across sex, age and tissue, and shows where the model fails.

On 192 held-out cell lines, 44.3% of the drugs in Sentinel's top-10 shortlist were truly sensitive, against 41.6% for the per-drug + tissue average and 20.3% for random drugs.

## Repository layout
| Path | Contents |
|---|---|
| `Project_Code/Sentinel.ipynb` | The whole project: data, baselines, final model, evaluation, drug shortlist and the Sentinel web app |
| `Project_Code/figures/` | Saved plots |
| `Project_Code/data/DATA_SOURCES.md` | Where the data comes from, usage terms and citations |

## How to run
Open `Project_Code/Sentinel.ipynb` in Google Colab and choose **Runtime → Run all** (about 1–2 minutes). Section 21 starts the Sentinel web app and prints a link to open it. The notebook downloads the public data from the Wellcome Sanger Institute automatically; no uploads or API keys are needed.

## Data
GDSC2 drug-response data and Cell Model Passports annotations, Wellcome Sanger Institute. Raw data is not stored in this repository (see `Project_Code/data/DATA_SOURCES.md` for sources, licence and citations).
