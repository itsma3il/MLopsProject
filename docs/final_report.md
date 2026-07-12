# Rapport final - Fraud Detection MLOps

## Résumé exécutif
Ce projet industrialise une solution de détection de fraude bancaire basée sur le dataset Kaggle Credit Card Fraud Detection. Le livrable couvre la chaîne DataOps, la qualité des données, le Machine Learning, le tracking MLflow, le serving FastAPI, la conteneurisation, la CI/CD, le monitoring et la documentation.

## Problème métier
Les fraudes représentent une faible proportion des transactions, mais elles ont un impact financier et opérationnel élevé. Le système vise à prioriser les transactions suspectes grâce à un score de fraude et un niveau de risque.

## Données
- Source: Kaggle `mlg-ulb/creditcardfraud`.
- Volume original: environ 284 807 transactions.
- Cible: `Class`, avec 1 pour fraude.
- Particularité: classes fortement déséquilibrées.

## DataOps
- dlt ingère le CSV Kaggle dans DuckDB.
- dbt nettoie, documente et transforme les données.
- Les tests dbt et le contrat de données vérifient schéma, valeurs obligatoires et labels.
- Dagster orchestre les étapes du pipeline.

## Machine Learning
- Préparation: nettoyage, suppression doublons, clipping `Amount`, feature engineering.
- Modèles testés: Logistic Regression, Decision Tree, Random Forest, XGBoost.
- Méthodologie: split train/validation/test, SMOTE uniquement dans les folds de CV, sélection sur validation, évaluation finale sur test.
- Artefacts: modèle, scaler, colonnes, métriques, statistiques de référence.

## MLOps
- MLflow trace paramètres, métriques, artefacts et modèle enregistré.
- FastAPI expose le modèle pour prédiction temps réel.
- PostgreSQL conserve l'historique des prédictions.
- `/metrics` expose disponibilité, latence et métriques ML simples.

## CI/CD et déploiement
- GitHub Actions lance tests unitaires, checks d'import, dbt parse et build container.
- Podman Compose démarre API, Streamlit, PostgreSQL, MLflow et Dagster.

## Limites
- Le dataset est anonymisé par PCA, ce qui limite l'interprétabilité métier.
- La surveillance de drift reste simple et doit être enrichie pour une production réelle.
- Le dataset Kaggle est statique; une vraie banque utiliserait un flux transactionnel continu.

## Améliorations futures
- Ajouter Evidently ou un module dédié pour le drift statistique.
- Ajouter authentification API et gestion des rôles.
- Ajouter des seuils de décision calibrés avec coût métier.
- Automatiser le réentraînement planifié dans Dagster.
