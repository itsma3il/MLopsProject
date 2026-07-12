# Architecture

## Vue d'ensemble
Le projet suit une chaîne DataOps/MLOps complète:

```text
Kaggle -> data/raw -> dlt -> DuckDB -> dbt -> sklearn/imblearn -> MLflow -> FastAPI -> Streamlit
                                      \-> dbt docs/tests
                         Dagster orchestre ingestion, transformation, training, evaluation, monitoring
```

## Composants
- Source: `kagglehub.dataset_download("mlg-ulb/creditcardfraud")`.
- Ingestion: `dataops/ingestion.py` charge le CSV dans `raw.creditcard_transactions`.
- Stockage analytique: DuckDB dans `data/warehouse/fraud.duckdb`.
- Transformations: `dbt_fraud` produit `stg_transactions` et `fraud_features`.
- Qualité: contrat YAML, validation Python, tests dbt `not_null` et `accepted_values`.
- Machine Learning: `src/train.py` exécute split stratifié, SMOTE dans la CV, sélection validation, évaluation test.
- Registry: MLflow tracke paramètres, métriques, artefacts et modèle enregistré.
- Serving: FastAPI expose `/health`, `/predict`, `/batch_predict`, `/metrics`, `/model/info`.
- Interface: Streamlit consomme l'API.
- Historique: PostgreSQL stocke les prédictions.
- Orchestration: Dagster matérialise les assets du pipeline.
- CI/CD: GitHub Actions teste et construit l'image container.

## Lineage
1. Kaggle dataset.
2. `data/raw/creditcard.csv`.
3. dlt vers `raw.creditcard_transactions`.
4. dbt `stg_transactions`.
5. dbt `fraud_features`.
6. `src/train.py` produit `models/best_model.joblib`, `metrics.json`, `reference_stats.json`.
7. MLflow enregistre expérience et modèle.
8. FastAPI sert les prédictions et écrit les événements de monitoring.

## Monitoring
- Disponibilité: `GET /health`.
- Temps de réponse: moyenne exposée par `/metrics`.
- Métriques ML runtime: taux de fraude, probabilité moyenne, volume de prédictions.
- Drift simple: comparaison possible avec `models/reference_stats.json` et les événements `data/monitoring/prediction_events.jsonl`.
