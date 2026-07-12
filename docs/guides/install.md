# Guide d'installation

## Prérequis
- Miniforge/conda avec l'environnement `ml-api`.
- Podman et Podman Compose.
- Compte Kaggle ou accès compatible avec `kagglehub`.
- Git.

## Environnement Python
```bash
cd fraud-detection
conda activate ml-api
pip install -r requirements.txt
```

## Dataset Kaggle
Le téléchargement officiel passe par:

```python
kagglehub.dataset_download("mlg-ulb/creditcardfraud")
```

Au premier entraînement ou à la première ingestion, le fichier est copié vers:

```text
data/raw/creditcard.csv
```

Ce fichier n'est pas versionné dans Git.

## Services locaux avec Podman
```bash
podman compose up --build
```

Services:
- FastAPI: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Streamlit: http://localhost:8501
- MLflow: http://localhost:5000
- Dagster: http://localhost:3000
- PostgreSQL: localhost:5432

## Commandes DataOps
```bash
python -m dataops.ingestion
cd dbt_fraud
dbt build --profiles-dir . --project-dir .
dbt docs generate --profiles-dir . --project-dir .
```

## Commandes MLOps
```bash
python -m src.train
python -m src.evaluate
dagster dev -m dagster_project.definitions
```
