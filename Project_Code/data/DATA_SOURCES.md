# Data Sources and Notes

All data in this project comes from the **Wellcome Sanger Institute** ([GDSC](https://www.cancerrxgene.org/) and [Cell Model Passports](https://cellmodelpassports.sanger.ac.uk/downloads)). It covers cancer cell lines grown in the lab and contains no patient records.

## Files used in `Team_Sentinel_Health_AI.ipynb`

| File | What it contains | Download URL |
|---|---|---|
| `GDSC2_fitted_dose_response_27Oct23.xlsx` | Drug response (`LN_IC50`), drug ID, drug name and putative target for 242,036 cell line x drug experiments | `https://cmp.cog.sanger.ac.uk/download/GDSC2_fitted_dose_response_27Oct23.xlsx` |
| `GDSC1_fitted_dose_response_27Oct23.xlsx` | The older, separate GDSC drug screen; used only for the outside check at the end of Section 28 | `https://cmp.cog.sanger.ac.uk/download/GDSC1_fitted_dose_response_27Oct23.xlsx` |
| `model_list_20261013.csv` | Cell line metadata (`model_id`, tissue, cancer type, patient sex and age at sampling) | `https://cog.sanger.ac.uk/cmp/download/model_list_20261013.csv` |
| `mutations_summary_20260724.zip` | Driver gene mutations per sequenced cell line | `https://cog.sanger.ac.uk/cmp/download/mutations_summary_20260724.zip` |
| `model_dataset_availability_20260727.csv` | Records which cell lines have whole-exome or whole-genome sequencing | `https://cog.sanger.ac.uk/cmp/download/model_dataset_availability_20260727.csv` |
| `rnaseq_merged_20260323.zip` | RNA-seq gene expression (TPM) per cell line, combining Sanger and Broad Institute (CCLE) data; Sanger data is used where a line was sequenced by both | `https://cog.sanger.ac.uk/cmp/download/rnaseq_merged_20260323.zip` |

## Data notes and cleaning steps

1. **Sequenced cell lines only.** A cell line missing from the mutation table might simply not have been sequenced. We check `model_dataset_availability_20260727.csv` first and keep the 965 sequenced cell lines.
2. **Non-cancer cell lines.** 7 sequenced lines are marked `Non-Cancerous` in `model_list_20261013.csv` and are removed before modelling, leaving 958 cancer cell lines and 239,081 drug-response rows.
3. **Drug IDs vs drug names.** 9 drug names were screened under two different `DRUG_ID` values, so we group and model by `DRUG_ID` (295 drugs).
4. **Excluded genes with repeated identical variants.** For 8 genes (`SDHA`, `CBLC`, `POLQ`, `KMT2C`, `HLA-A`, `HLA-B`, `PABPC1`, `CLTCL1`), most listed mutations are the exact same DNA/protein change across unrelated cell lines (likely germline variants or sequencing artefacts). We leave these 8 genes out and keep the remaining 84 genes mutated in at least 20 cell lines.
5. **Dose ranges.** Each drug was tested over its own concentration range, and in 71.8% of rows the fitted `IC50` is above the highest concentration tested. Raw `ln(IC50)` values are therefore always compared against that drug's own training average.

6. **Gene expression.** Not every cell line has RNA-seq data. Expression features are built from the training cell lines only (most variable genes, scaling and PCA), and lines without expression are filled with their tissue's training average plus a 0/1 flag.

## Usage policy

Under the [Sanger DepMap Data Usage Policy](https://depmap.sanger.ac.uk/documentation/data-usage-policy/), the data is free to use for academic and educational research but should not be redistributed. For that reason, raw files are not committed to this repository; `Team_Sentinel_Health_AI.ipynb` downloads them directly from Sanger when run.

## Citations

**Data papers**
1. Yang W, et al. Genomics of Drug Sensitivity in Cancer (GDSC): a resource for therapeutic biomarker discovery in cancer cells. *Nucleic Acids Research* 41(D1):D955–D961, 2013. https://doi.org/10.1093/nar/gks1111
2. Iorio F, et al. A Landscape of Pharmacogenomic Interactions in Cancer. *Cell* 166(3):740–754, 2016. https://doi.org/10.1016/j.cell.2016.06.017
3. van der Meer D, et al. Cell Model Passports — a hub for clinical, genetic and functional datasets of preclinical cancer models. *Nucleic Acids Research* 47(D1):D923–D929, 2019. https://doi.org/10.1093/nar/gky872
4. Ghandi M, et al. Next-generation characterization of the Cancer Cell Line Encyclopedia. *Nature* 569:503–508, 2019. https://doi.org/10.1038/s41586-019-1186-3 (Broad Institute RNA-seq in the merged expression file)

**Methods**
5. Ke G, et al. LightGBM: A Highly Efficient Gradient Boosting Decision Tree. *Advances in Neural Information Processing Systems* 30, 2017. [Link](https://proceedings.neurips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html)
6. Friedman JH. Greedy function approximation: a gradient boosting machine. *Annals of Statistics* 29(5):1189–1232, 2001. https://doi.org/10.1214/aos/1013203451
7. Hoerl AE, Kennard RW. Ridge Regression: Biased Estimation for Nonorthogonal Problems. *Technometrics* 12(1):55–67, 1970. https://doi.org/10.1080/00401706.1970.10488634
8. Jolliffe IT, Cadima J. Principal component analysis: a review and recent developments. *Philosophical Transactions of the Royal Society A* 374:20150202, 2016. https://doi.org/10.1098/rsta.2015.0202
9. Pedregosa F, et al. Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research* 12:2825–2830, 2011. [Link](https://jmlr.org/papers/v12/pedregosa11a.html) (cross-validation by group: [scikit-learn guide](https://scikit-learn.org/stable/modules/cross_validation.html))

**Biology behind the drug–gene checks**
10. Hauschild A, et al. Dabrafenib in BRAF-mutated metastatic melanoma: a multicentre, open-label, phase 3 randomised controlled trial. *The Lancet* 380(9839):358–365, 2012. https://doi.org/10.1016/S0140-6736(12)60868-X
11. Vassilev LT, et al. In Vivo Activation of the p53 Pathway by Small-Molecule Antagonists of MDM2. *Science* 303(5659):844–848, 2004. https://doi.org/10.1126/science.1092472
12. Lynch TJ, et al. Activating Mutations in the Epidermal Growth Factor Receptor Underlying Responsiveness of Non–Small-Cell Lung Cancer to Gefitinib. *New England Journal of Medicine* 350:2129–2139, 2004. https://doi.org/10.1056/NEJMoa040938
13. André F, et al. Alpelisib for PIK3CA-Mutated, Hormone Receptor–Positive Advanced Breast Cancer. *New England Journal of Medicine* 380:1929–1940, 2019. https://doi.org/10.1056/NEJMoa1813904

**Software**
14. McKinney W. Data Structures for Statistical Computing in Python. *Proceedings of the 9th Python in Science Conference*, 56–61, 2010. https://doi.org/10.25080/Majora-92bf1922-00a ([pandas](https://pandas.pydata.org))
15. Harris CR, et al. Array programming with NumPy. *Nature* 585:357–362, 2020. https://doi.org/10.1038/s41586-020-2649-2 ([NumPy](https://numpy.org))
16. Hunter JD. Matplotlib: A 2D Graphics Environment. *Computing in Science & Engineering* 9(3):90–95, 2007. https://doi.org/10.1109/MCSE.2007.55 ([Matplotlib](https://matplotlib.org))
17. Waskom ML. seaborn: statistical data visualization. *Journal of Open Source Software* 6(60):3021, 2021. https://doi.org/10.21105/joss.03021 ([Seaborn](https://seaborn.pydata.org))
18. Abid A, et al. Gradio: Hassle-Free Sharing and Testing of ML Models in the Wild. arXiv:1906.02569, 2019. https://arxiv.org/abs/1906.02569 ([Gradio](https://www.gradio.app))
Also used: [Python](https://www.python.org), [scikit-learn](https://scikit-learn.org), [LightGBM](https://lightgbm.readthedocs.io), [Google Colab](https://colab.research.google.com).

Coding assistants (Claude / Gemini) were used to help find Sanger download URLs, check data merges and structure the notebook.
