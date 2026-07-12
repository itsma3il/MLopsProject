# Gestion Agile

## Rôles
- Product Owner: Ismail Mousdik.
- Scrum Master: Anass erfoudi.
- Data Engineer: Oussama Jounaidi, Hamza.
- ML Engineer: Kawtar El Bejjaji, Khalid.
- Data Analyst: Rihab El Mrikh.

## Product Backlog
| ID | User Story | Priorité | Critère d'acceptation |
| --- | --- | --- | --- |
| US-01 | En tant qu'analyste fraude, je veux soumettre une transaction pour obtenir un score de fraude. | Haute | `POST /predict` retourne prediction, probabilité et niveau de risque. |
| US-02 | En tant que Data Engineer, je veux ingérer le dataset Kaggle dans DuckDB. | Haute | dlt crée `raw.creditcard_transactions`. |
| US-03 | En tant que Data Analyst, je veux une table transformée et documentée. | Haute | dbt construit `fraud_features` avec tests valides. |
| US-04 | En tant que ML Engineer, je veux tracker les expériences. | Haute | MLflow contient paramètres, métriques, artefacts et modèle. |
| US-05 | En tant qu'utilisateur métier, je veux une interface simple. | Moyenne | Streamlit consomme l'API et affiche le résultat. |
| US-06 | En tant qu'équipe projet, je veux un pipeline orchestré. | Haute | Dagster matérialise ingestion, dbt, training, evaluation, monitoring. |
| US-07 | En tant que mainteneur, je veux des tests CI/CD. | Haute | GitHub Actions exécute tests et build container. |
| US-08 | En tant qu'exploitant, je veux surveiller le service. | Moyenne | `/metrics` expose disponibilité, latence et métriques ML simples. |

## Sprint 1 - Cadrage et baseline ML
- Objectif: livrer le modèle initial, l'API et la compréhension des données.
- Travaux: EDA, preprocessing, entraînement sans leakage, FastAPI, Streamlit.
- Review: démonstration d'une prédiction et lecture des métriques.
- Retrospective: renforcer la traçabilité et séparer DataOps/MLOps.

## Sprint 2 - DataOps et qualité
- Objectif: industrialiser la donnée.
- Travaux: Kaggle loader, dlt, DuckDB, dbt, data contract, tests qualité, lineage.
- Review: démonstration `dlt -> DuckDB -> dbt build`.
- Retrospective: ajouter un fixture sample pour CI afin d'éviter la dépendance Kaggle.

## Sprint 3 - MLOps, déploiement et monitoring
- Objectif: rendre le projet livrable et exploitable.
- Travaux: MLflow, Dagster, `/metrics`, Docker/Podman Compose, GitHub Actions, docs, rapport.
- Review: démonstration end-to-end et consultation MLflow/Dagster.
- Retrospective: documenter les limites du dataset et les prochaines améliorations.
