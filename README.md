# 🛡️ Fraud Detection System

Système intelligent de détection de fraude dans les transactions financières par Machine Learning.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

---

## Table des matières

- [Comment ça marche](#comment-ça-marche)
- [Architecture du projet](#architecture-du-projet)
- [Installation](#installation)
- [Lancer l'application](#lancer-lapplication)
- [Pipeline ML en détail](#pipeline-ml-en-détail)
- [API REST](#api-rest)
- [Frontend Streamlit](#frontend-streamlit)
- [Docker (tout-en-un)](#docker-tout-en-un)
- [Tests](#tests)
- [Résultats du modèle](#résultats-du-modèle)
- [Déploiement](#déploiement)
- [MLOps & DataOps](#mlops--dataops)

---

## Comment ça marche

Le système fonctionne en 3 couches :

```mermaid
flowchart TB
    Frontend["Streamlit frontend<br/>Prediction form<br/>Batch CSV upload<br/>Analytics dashboard<br/>Prediction history"]
    API["FastAPI service<br/>Input validation<br/>Feature engineering<br/>ML pipeline inference<br/>Risk score response"]
    DB[("PostgreSQL<br/>Prediction history<br/>Retrospective analysis")]

    Frontend -->|"HTTP<br/>8501 to 8000"| API
    API -->|"SQL<br/>5432"| DB
```

### Flux de prédiction

```mermaid
flowchart LR
    Raw["Raw transaction<br/>Time, Amount, V1-V28"]
    Features["Feature engineering<br/>9 derived features"]
    Align["Column alignment<br/>39 expected features"]
    Pipeline["ML pipeline<br/>RobustScaler + classifier"]
    Result["Prediction output<br/>prediction, probability, risk level"]
    History[("PostgreSQL<br/>prediction history")]

    Raw --> Features --> Align --> Pipeline --> Result --> History
```

Le modèle sauvegardé est un **pipeline complet** (`imblearn.Pipeline`) qui contient :
1. **RobustScaler** — normalise les features
2. **SMOTE** — (actif uniquement à l'entraînement, ignoré en prédiction)
3. **RandomForestClassifier** — classifie la transaction

Aucun scaling manuel n'est nécessaire à la prédiction : le pipeline gère tout.

---

## Architecture du projet

```mermaid
flowchart TB
    Root["MLopsProject"]

    Root --> Config["config/<br/>Central settings"]
    Root --> Src["src/"]
    Root --> Ops["Operational entrypoints"]
    Root --> Data["data/<br/>Raw, processed, warehouse"]
    Root --> Models["models/<br/>Generated ML artifacts"]
    Root --> Docs["docs/<br/>Guides, architecture, project, reports"]
    Root --> Tests["tests/<br/>Unit and integration"]
    Root --> Reports["reports/latex<br/>Academic report"]
    Root --> Runtime["Dockerfile<br/>docker-compose.yml<br/>requirements.txt"]

    Src --> CoreData["core/data<br/>Kaggle loader, preprocessing, features, ingestion"]
    Src --> CoreModels["core/models<br/>Training, evaluation, prediction, metrics"]
    Src --> CoreMonitoring["core/monitoring<br/>Metrics and drift helpers"]
    Src --> CorePipeline["core/pipeline<br/>Runner, dashboard, diagrams"]
    Src --> ApiImpl["api<br/>FastAPI implementation"]
    Src --> DbImpl["db<br/>SQLAlchemy implementation"]
    Src --> Utils["utils<br/>Data contract and shared helpers"]

    Ops --> ApiCompat["api/<br/>uvicorn compatibility wrappers"]
    Ops --> DbCompat["db/<br/>legacy DB import wrappers"]
    Ops --> DataOpsCompat["dataops/<br/>ingestion CLI wrapper"]
    Ops --> MonitoringCompat["monitoring/<br/>monitoring wrappers"]
    Ops --> Webapp["webapp/<br/>Streamlit app"]
    Ops --> Dbt["dbt_fraud/<br/>dbt transformations/tests"]
    Ops --> Dagster["dagster_project/<br/>orchestration assets"]
```

### MLOps & DataOps

Le projet contient maintenant les livrables MLOps/DataOps demandés par le module:

- **dlt + DuckDB**: `python -m dataops.ingestion`
- **dbt**: projet `dbt_fraud/` avec staging, mart, tests et lineage
- **Dagster**: `dagster dev -m dagster_project.definitions`
- **MLflow**: tracking et registry lors de `python -m src.train`
- **Monitoring**: `GET /metrics` et `GET /model/info`
- **Data Contract**: `contracts/creditcard_fraud_contract.yml`
- **Documentation**: `docs/project/vision.md`, `docs/project/agile.md`, `docs/architecture/architecture.md`, `docs/guides/install.md`, `docs/guides/usage.md`, `docs/guides/colab_training_guide.md`, `docs/architecture/model_accuracy_diagnosis.md`, `docs/project/final_report.md`, `docs/project/repository_structure.md`

Commandes principales:

```bash
python -m dataops.ingestion
cd dbt_fraud && dbt build --profiles-dir . --project-dir . && cd ..
python -m src.train
python -m src.evaluate
podman compose up --build
```

---

## Installation

### Prérequis

- Python 3.11+
- PostgreSQL (optionnel en local, inclus dans Docker)
- Docker & Docker Compose (optionnel, pour le déploiement tout-en-un)

### Installation locale

```bash
# 1. Cloner le projet
git clone https://github.com/votre-username/fraud-detection.git
cd fraud-detection

# 2. Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Installer les dépendances
pip install -r requirements.txt
```

### Dataset

Le dataset est le [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) de Kaggle (284 807 transactions, 492 fraudes).

**Option A** — Téléchargement automatique (nécessite un compte Kaggle configuré) :
```bash
python -m src.train
# Le script télécharge automatiquement le dataset via kagglehub
```

**Option B** — Téléchargement manuel :
1. Télécharger `creditcard.csv` depuis [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
2. Le placer dans `data/raw/creditcard.csv`

---

## Lancer l'application

### Étape 1 : Entraîner le modèle

```bash
python -m src.train
```

Cela exécute le pipeline complet :
- Chargement et nettoyage des données
- Feature engineering (9 features dérivées)
- Split stratifié train/test (80/20)
- Entraînement de 4 modèles avec cross-validation (Scale + SMOTE inside CV)
- Sélection du meilleur modèle (par F1-score)
- Évaluation sur le test set intouché
- Sauvegarde des artefacts dans `models/`

Durée : ~5-10 minutes selon la machine.

### Étape 2 : Lancer PostgreSQL

```bash
# Avec Docker (recommandé)
docker run -d --name fraud-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=fraud_detection \
  -p 5432:5432 \
  postgres:16-alpine
```

Ou installer PostgreSQL localement et créer la base `fraud_detection`.

> **Note** : L'API fonctionne même sans PostgreSQL (les prédictions marchent, seul l'historique est désactivé).

### Étape 3 : Lancer l'API

```bash
uvicorn api.main:app --reload --port 8000
```

L'API est accessible sur : http://localhost:8000
Documentation Swagger : http://localhost:8000/docs

### Étape 4 : Lancer le frontend

```bash
streamlit run webapp/app.py
```

Interface web : http://localhost:8501

### Tout-en-un avec Docker Compose

```bash
docker-compose up --build
```

Cela lance les 3 services automatiquement :
- **API** : http://localhost:8000
- **Frontend** : http://localhost:8501
- **PostgreSQL** : localhost:5432

---

## Pipeline ML en détail

### Méthodologie anti-leakage

```mermaid
flowchart TD
    Raw["Raw data"]
    Clean["Clean data<br/>remove duplicates, remove NaN, cap Amount P99"]
    FE["Feature engineering<br/>on raw values before split"]
    Split["Stratified split<br/>train, validation, untouched test"]
    CV["Cross-validation on train set"]
    Scale["RobustScaler<br/>fit inside each fold"]
    SMOTE["SMOTE<br/>train fold only"]
    Classifier["Classifier training"]
    Select["Best model selection<br/>validation PR-AUC/F1"]
    Threshold["Decision threshold optimization<br/>validation set only"]
    Test["Final evaluation<br/>untouched test set"]
    Save["Save complete pipeline<br/>model, threshold, metrics, features"]

    Raw --> Clean --> FE --> Split --> CV
    CV --> Scale --> SMOTE --> Classifier --> Select
    Split --> Threshold
    Select --> Threshold --> Test --> Save
```

### Features engineered (9)

| Feature | Description |
|---------|-------------|
| `transaction_hour` | Heure extraite de Time (sec → heures mod 24) |
| `day_period` | 0=nuit, 1=matin, 2=après-midi, 3=soir |
| `amount_log` | log1p(Amount) — réduit l'asymétrie |
| `amount_bin` | 0=low(<50), 1=medium(<200), 2=high(<1000), 3=very_high |
| `v_mean` | Moyenne des V1-V28 |
| `v_std` | Écart-type des V1-V28 |
| `risk_score` | Combinaison des V les plus discriminants |
| `amount_x_v14` | Interaction Amount × |V14| |
| `amount_x_v17` | Interaction Amount × |V17| |

### Modèles comparés

4 modèles sont entraînés avec `RandomizedSearchCV` :
- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost

Chaque modèle est un `imblearn.Pipeline` contenant `RobustScaler + SMOTE + Classifier`.

### Niveaux de risque

| Probabilité | Niveau |
|-------------|--------|
| < 0.3 | LOW |
| 0.3 – 0.6 | MEDIUM |
| 0.6 – 0.8 | HIGH |
| ≥ 0.8 | CRITICAL |

---

## API REST

### Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Informations de l'API |
| GET | `/health` | Health check (statut + modèle chargé) |
| POST | `/predict` | Prédiction unique |
| POST | `/batch_predict` | Prédiction batch (max 1000) |
| GET | `/predictions/history` | Historique depuis PostgreSQL |

### Exemple : prédiction unique

**Requête :**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Time": 0,
    "Amount": 149.62,
    "V1": -1.36, "V2": -0.07, "V3": 2.54, "V4": 1.38,
    "V5": 0, "V6": 0, "V7": 0, "V8": 0, "V9": 0,
    "V10": 0, "V11": 0, "V12": 0, "V13": 0, "V14": -5.0,
    "V15": 0, "V16": 0, "V17": -3.0, "V18": 0, "V19": 0,
    "V20": 0, "V21": 0, "V22": 0, "V23": 0, "V24": 0,
    "V25": 0, "V26": 0, "V27": 0, "V28": 0
  }'
```

**Réponse :**
```json
{
  "prediction": 0,
  "is_fraud": false,
  "fraud_probability": 0.1646,
  "risk_level": "LOW"
}
```

### Exemple : prédiction batch

```bash
curl -X POST http://localhost:8000/batch_predict \
  -H "Content-Type: application/json" \
  -d '{"transactions": [{"Time": 0, "Amount": 100, "V1": 0, ...}, ...]}'
```

**Réponse :**
```json
{
  "predictions": [...],
  "total": 2,
  "fraud_count": 0,
  "fraud_rate": 0.0
}
```

### Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/fraud_detection` | URL de connexion PostgreSQL |
| `API_HOST` | `0.0.0.0` | Hôte de l'API |
| `API_PORT` | `8000` | Port de l'API |
| `API_URL` | `http://localhost:8000` | URL de l'API (pour Streamlit) |

---

## Frontend Streamlit

L'interface web comporte 4 pages :

### 1. Prédiction
- Formulaire avec montant et features V1-V28 (aléatoires ou zéros)
- Affiche : résultat, probabilité, niveau de risque
- Jauge visuelle Plotly du score de risque

### 2. Upload CSV
- Upload d'un fichier CSV avec les colonnes `Time, V1-V28, Amount`
- Prédiction batch par lots de 100
- Barre de progression
- Tableau des résultats avec métriques agrégées

### 3. Historique
- Affiche les prédictions passées depuis PostgreSQL
- Tableau avec timestamp, montant, résultat, probabilité, risque

### 4. Dashboard
- Métriques globales (total, fraudes, taux, montant moyen)
- Graphique en camembert des niveaux de risque
- Histogramme de distribution des probabilités

---

## Docker (tout-en-un)

### Lancer

```bash
docker-compose up --build
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| `api` | 8000 | FastAPI + modèle ML |
| `webapp` | 8501 | Interface Streamlit |
| `db` | 5432 | PostgreSQL 16 |

### Arrêter

```bash
docker-compose down          # Arrête les conteneurs
docker-compose down -v       # Arrête + supprime les volumes (données DB)
```

### Réseau interne

- Le frontend communique avec l'API via `http://api:8000` (DNS Docker)
- L'API communique avec PostgreSQL via `db:5432`

---

## Tests

```bash
pytest tests/ -v
```

10 tests couvrent :
- **Preprocessing** : nettoyage, scaler, scaling
- **Feature Engineering** : création des 9 features, absence de NaN
- **API** : root, health, validation input, gestion modèle non chargé

---

## Résultats du modèle

Meilleur modèle sélectionné : **Random Forest** (CV F1 = 0.842)

### Métriques sur le test set (20% des données, intouché)

| Métrique | Valeur |
|----------|--------|
| Accuracy | 99.95% |
| Precision | 90.5% |
| Recall | 80.0% |
| F1-Score | 84.9% |
| ROC-AUC | 97.2% |
| PR-AUC | 81.8% |

### Matrice de confusion

|  | Prédit Légitime | Prédit Fraude |
|--|-----------------|---------------|
| **Réel Légitime** | 56 643 | 8 |
| **Réel Fraude** | 19 | 76 |

---

## Déploiement

### Render / Railway

1. Connecter le repo GitHub
2. Variables d'environnement : `DATABASE_URL` (PostgreSQL externe)
3. Build command : `pip install -r requirements.txt`
4. Start command : `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Commandes utiles

```bash
# Ré-entraîner le modèle
python -m src.train

# Évaluer le modèle (recharge test set + recalcule métriques)
python -m src.evaluate

# Lancer l'API seule
uvicorn api.main:app --reload --port 8000

# Lancer le frontend seul
streamlit run webapp/app.py

# Lancer les tests
pytest tests/ -v

# Docker complet
docker-compose up --build
```

---

## Licence

MIT
