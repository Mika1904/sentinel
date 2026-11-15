# Sentinel app (hosted version)

A standalone version of the app in Section 29 of `Project_Code/Team_Sentinel_Health_AI.ipynb`, deployed on Render with `render.yaml` in the repository root.

- `model_bundle.joblib` is saved by the notebook (Section 29). It holds only the fitted final model and summary statistics, not the raw Sanger data.
- Predictions are identical to the notebook's. Each drug's percentile is read from a 1%-step summary of its training results instead of the raw values, so the order of drugs with very close scores can differ slightly from the notebook.
- Run it locally with `python app/app.py` (after `pip install -r app/requirements.txt`).

*Research prototype on lab cell lines, not medical advice. Data: GDSC2 and Cell Model Passports, Wellcome Sanger Institute, used under the Sanger DepMap Data Usage Policy for educational, non-commercial purposes.*
