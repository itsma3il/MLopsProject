# Vision du projet

## Problématique
Les transactions bancaires frauduleuses sont rares, coûteuses et difficiles à détecter manuellement. Le projet vise à transformer un dataset brut de transactions en produit IA exploitable pour identifier les transactions à risque en temps quasi réel.

## Objectifs
- Construire un pipeline reproductible depuis Kaggle jusqu'au modèle ML.
- Détecter les fraudes avec un modèle de classification supervisée.
- Exposer le modèle via FastAPI et une interface Streamlit.
- Industrialiser le cycle de vie avec DataOps, MLOps, CI/CD, monitoring et documentation.

## Utilisateurs cibles
- Analystes fraude qui inspectent les alertes.
- Equipe risque bancaire qui suit les indicateurs de fraude.
- Equipe Data/ML qui maintient les pipelines et le modèle.
- Enseignant/evaluateur qui vérifie les livrables MLOps/DataOps.

## Valeur métier
- Réduction du temps de détection des fraudes.
- Priorisation des transactions les plus risquées.
- Traçabilité des prédictions et des versions de modèle.
- Base industrialisable pour surveillance de drift et réentrainement.

## Data Strategy
- Source officielle: Kaggle `mlg-ulb/creditcardfraud` via `kagglehub`.
- Cache local non versionné: `data/raw/creditcard.csv`.
- Entrepôt local: DuckDB `data/warehouse/fraud.duckdb`.
- Transformations: dbt, avec tests et lineage.
- Contrat de données: `contracts/creditcard_fraud_contract.yml`.
- Tracking et registry: MLflow.
- Orchestration: Dagster.
