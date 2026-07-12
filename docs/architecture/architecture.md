# Architecture

## Vue d'ensemble
Le projet suit une chaîne DataOps/MLOps complète:

```mermaid
flowchart LR
    Kaggle[("Kaggle<br/>mlg-ulb/creditcardfraud")]
    Raw["data/raw<br/>creditcard.csv"]
    DLT["dlt ingestion"]
    DuckDB[("DuckDB<br/>data/warehouse/fraud.duckdb")]
    DBT["dbt<br/>staging, marts, tests, docs"]
    ML["sklearn + imblearn<br/>training/evaluation"]
    MLflow["MLflow<br/>tracking + registry"]
    API["FastAPI<br/>prediction service"]
    Streamlit["Streamlit<br/>demo UI"]
    Monitoring["Monitoring<br/>metrics + drift references"]
    Dagster["Dagster<br/>orchestration"]

    Kaggle --> Raw --> DLT --> DuckDB --> DBT --> ML --> MLflow --> API --> Streamlit
    API --> Monitoring
    DBT --> DBTDocs["dbt docs + lineage"]

    Dagster -. orchestrates .-> Raw
    Dagster -. orchestrates .-> DLT
    Dagster -. orchestrates .-> DBT
    Dagster -. orchestrates .-> ML
    Dagster -. orchestrates .-> Monitoring
```

## Composants
- Source: `kagglehub.dataset_download("mlg-ulb/creditcardfraud")`.
- Ingestion: `src/core/data/ingestion.py` charge le CSV dans `raw.creditcard_transactions`.
- Stockage analytique: DuckDB dans `data/warehouse/fraud.duckdb`.
- Transformations: `dbt_fraud` produit `stg_transactions` et `fraud_features`.
- Qualité: contrat YAML, validation Python, tests dbt `not_null` et `accepted_values`.
- Machine Learning: `src/core/models/train.py` exécute split stratifié, SMOTE dans la CV, sélection validation, évaluation test.
- Registry: MLflow tracke paramètres, métriques, artefacts et modèle enregistré.
- Serving: FastAPI expose `/health`, `/predict`, `/batch_predict`, `/metrics`, `/model/info`.
- Interface: Streamlit consomme l'API.
- Historique: PostgreSQL stocke les prédictions.
- Orchestration: Dagster matérialise les assets du pipeline.
- CI/CD: GitHub Actions teste et construit l'image container.

## Lineage

```mermaid
flowchart TD
    Source["Kaggle dataset"]
    Cache["data/raw/creditcard.csv"]
    RawTable["DuckDB raw.creditcard_transactions"]
    Staging["dbt stg_transactions"]
    Mart["dbt fraud_features"]
    Train["src/core/models/train.py"]
    Artifacts["models/<br/>best_model.joblib<br/>metrics.json<br/>reference_stats.json"]
    Registry["MLflow run + registered model"]
    Serving["FastAPI predictions"]
    Events["data/monitoring/prediction_events.jsonl"]

    Source --> Cache --> RawTable --> Staging --> Mart --> Train
    Train --> Artifacts
    Train --> Registry
    Artifacts --> Serving
    Serving --> Events
```

## Monitoring
- Disponibilité: `GET /health`.
- Temps de réponse: moyenne exposée par `/metrics`.
- Métriques ML runtime: taux de fraude, probabilité moyenne, volume de prédictions.
- Drift simple: comparaison possible avec `models/reference_stats.json` et les événements `data/monitoring/prediction_events.jsonl`.
