# Rapport — Notebook 05: Imbalanced Experiments

Résumé et guide d'exécution pour le notebook `notebooks/05_imbalanced_experiments.ipynb`.

**Fichier généré automatiquement.**

## 1. Objectif
Comparer plusieurs stratégies de gestion du déséquilibre de classes pour la détection de fraudes, en privilégiant des métriques adaptées au déséquilibre : PR-AUC (average precision), F1-score et Recall. Tester aussi des approches non supervisées (IsolationForest, OneClassSVM) pour comparaison.

## 2. Contrainte méthodologique
- Aucune fuite d'information (no data leakage).
- Le prétraitement (`RobustScaler`) est fit uniquement sur le jeu d'entraînement.
- Test set utilisé UNE SEULE FOIS, en fin de processus.
- SMOTE appliqué uniquement sur l'entraînement lorsque testé.
- Optimisation du seuil (threshold) faite uniquement sur la validation.
- Répétabilité via `RANDOM_STATE=42`.

## 3. Données
Le notebook charge `data/raw/creditcard.csv` et effectue : dédoublonnage, clipping des outliers sur `Amount` (99e percentile), puis split en :
- Train: 60%
- Validation: 20%
- Test: 20%

Les jeux sont stratifiés sur la classe cible `Class`.

## 4. Pipeline expérimental
1. Chargement + nettoyage
2. Split train/val/test (stratifié)
3. Scaling: `RobustScaler` fit sur `X_train` puis appliqué à val/test
4. Baselines (aucun traitement du déséquilibre)
5. Stratégies de déséquilibre testées :
   - Class weights (`class_weight='balanced'` ou `scale_pos_weight` pour XGB/LGBM)
   - SMOTE (resampling sur `X_train` uniquement)
   - BalancedRandomForest (implémentation imbalanced-learn)
6. Modèles avancés (tuned): XGB, LGBM, RandomForest (paramètres fournis)
7. Optimisation du seuil sur validation via F1
8. Évaluation finale unique sur test (avec seuil choisi)

## 5. Modèles évalués
- Logistic Regression (baseline, weighted)
- Decision Tree
- Random Forest (baseline, weighted, SMOTE)
- XGBoost (baseline, weighted, SMOTE, tuned)
- LightGBM (tuned)
- BalancedRandomForest (imblearn)
- IsolationForest, OneClassSVM (anomaly detection)

## 6. Métriques calculées
Pour chaque évaluation :
- F1, Precision, Recall
- PR-AUC (average precision)
- ROC-AUC
- Matrice de confusion (TN, FP, FN, TP)
- Seuil optimal sur validation (max F1) quand applicable

## 7. Résultats attendus et visualisations
Le notebook produit :
- Un tableau final trié par F1 (DataFrame `df_display`).
- Courbes Precision-Recall pour modèles principaux.
- Barplots comparant F1 / PR-AUC / Recall.
- Table des thresholds optimaux et performances associées.

> Remarque : les valeurs exactes dépendent des seeds et du paramétrage.

## 8. Exécution et reproduction
Recommandation pour exécuter localement (Windows PowerShell) :

```powershell
# activer venv
.\.venv\Scripts\Activate.ps1
# installer dépendances
pip install -r requirements.txt
# lancer Jupyter Lab/Notebook
jupyter lab
# ouvrir notebooks/05_imbalanced_experiments.ipynb
```

Ou exécution cellulaire séquentielle depuis l'IDE pour surveiller temps de calcul et mémoire.

## 9. Observations et recommandations (à valider par exécution)
- Les classifieurs boostés (XGB/LGBM) avec `scale_pos_weight` offrent souvent le meilleur compromis PR-AUC / F1 sur ce dataset.
- SMOTE peut améliorer rappel mais provoquer plus de faux positifs sur certains modèles; comparer toujours sur validation non rebalancée.
- L'optimisation du seuil sur validation donne un gain opérationnel majeur ; N’optimiser qu’avec la validation.
- Pour production : utiliser `ColumnTransformer` + pipeline scikit-learn, scaler et transformateurs sérialisés, et monitorer dérive des features.

## 10. Fichiers produits par le notebook
- Aucun fichier automatique par défaut, sauf si l'utilisateur ajoute une sauvegarde (`.csv` ou `.joblib`).
- Recommandation : exporter `df_display` et `df_final` vers `models/metrics_experiments_05.csv` pour archivage.

## 11. Prochaines étapes proposées
- Sauvegarder `df_final` et `df_thresholds` dans `models/` pour traçabilité.
- Générer un rapport HTML (nbconvert) pour partage.
- Automatiser l'exécution en mode batch (script Python) pour répéter expériences avec seeds multiples.

---
Fini — fichier : `docs/reports/REPORT_05_Imbalanced_Experiments.md`.
