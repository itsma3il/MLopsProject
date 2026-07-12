# Google Colab Training Guide

## Purpose

Use this workflow when the local PC cannot train the fraud detection model. The Colab notebook runs the same project training and evaluation code, then exports the trained artifacts and documentation bundle back to Google Drive.

Notebook:

```text
notebooks/colab/06_colab_training_evaluation.ipynb
```

## What Colab Produces

The notebook creates two zip files in:

```text
Google Drive / MyDrive / fraud-detection-mlops-exports
```

### 1. Model Artifacts Zip

Name pattern:

```text
fraud_model_artifacts_YYYYMMDD_HHMMSS.zip
```

Contains:

```text
best_model.joblib
scaler.joblib
feature_columns.json
metrics.json
decision_threshold.json
reference_stats.json
```

These files are required to run the local API with the trained model.

After downloading, extract the files into:

```text
fraud-detection/models/
```

### 2. Documentation Bundle Zip

Name pattern:

```text
fraud_documentation_bundle_YYYYMMDD_HHMMSS.zip
```

Contains:

```text
docs/
figures/
contracts/
dbt_fraud/models/
README.md
QUICK_START.md
requirements-colab.txt
requirements.txt
notebooks/colab/06_colab_training_evaluation.ipynb
```

Use this bundle for the academic report and presentation screenshots.

## Recommended Workflow

### Step 1 - Push or Zip the Project

Recommended:

```bash
git add .
git commit -m "prepare colab training"
git push
```

Then set this in the notebook:

```python
GITHUB_REPO_URL = "https://github.com/<user>/<repo>.git"
```

Alternative:

```bash
cd ..
zip -r MLopsProject.zip MLopsProject \
  -x "MLopsProject/data/raw/*" \
  -x "MLopsProject/data/warehouse/*" \
  -x "MLopsProject/.git/*" \
  -x "MLopsProject/__pycache__/*" \
  -x "MLopsProject/*/__pycache__/*"
```

Upload that zip in the notebook when asked.

## Step 2 - Run the Notebook

Open:

```text
notebooks/colab/06_colab_training_evaluation.ipynb
```

Run all cells in order.

The notebook will:

1. Mount Google Drive.
2. Clone or upload the project.
3. Install `requirements-colab.txt`.
4. Download the Kaggle dataset with `kagglehub`.
5. Run `run_training_pipeline()`.
6. Run `run_evaluation()`.
7. Save confusion matrix and metrics figures.
8. Export model and documentation zips to Drive.

## Step 3 - Bring Artifacts Back Locally

Download:

```text
fraud_model_artifacts_*.zip
```

Extract into:

```text
MLopsProject/models/
```

Then test locally:

```bash
cd MLopsProject
conda activate ml-api
python -m src.evaluate
uvicorn api.main:app --reload --port 8000
```

Check:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/model/info
curl http://localhost:8000/metrics
```

## Metrics to Report

Do not center the report around accuracy. For this fraud dataset, accuracy is misleading because the fraud class is extremely rare.

Report these metrics instead:

- `pr_auc`
- `recall`
- `precision`
- `f1_score`
- `balanced_accuracy`
- `mcc`
- `false_negative_rate`
- `false_positive_rate`
- confusion matrix
- selected `decision_threshold`

The explanation is documented in:

```text
docs/architecture/model_accuracy_diagnosis.md
```

## Expected Screenshots for the Final Report

Capture these from Colab:

- Training completion cell with best model.
- `metrics.json` printed output.
- Confusion matrix figure.
- Main metrics bar chart.
- Export zip paths in Google Drive.

Capture these locally after importing artifacts:

- `GET /health`.
- `GET /model/info`.
- `GET /metrics`.
- Swagger `/docs`.
- Streamlit prediction page.

## Notes

- Colab CPU is sufficient but training can take time.
- GPU is not required for scikit-learn RandomForest, but may help if XGBoost uses compatible settings.
- The full Kaggle CSV is not exported back by default to avoid large files.
- `data/raw/creditcard.csv` remains a generated local cache and should not be committed.
