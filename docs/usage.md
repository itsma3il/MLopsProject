# Guide d'utilisation

## Démo rapide
1. Démarrer les services:
   ```bash
   podman compose up --build
   ```
2. Ouvrir Swagger: http://localhost:8000/docs.
3. Tester `GET /health`.
4. Envoyer une transaction à `POST /predict`.
5. Consulter Streamlit: http://localhost:8501.
6. Consulter MLflow: http://localhost:5000.
7. Consulter Dagster: http://localhost:3000.

## Exemple API
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Time": 0,
    "Amount": 149.62,
    "V1": -1.359807,
    "V2": 0.072781,
    "V3": 2.536347,
    "V4": 1.378155
  }'
```

Les champs `V5` à `V28` ont des valeurs par défaut à 0 dans le schéma API.

## Pipeline complet
```bash
python -m dataops.ingestion
cd dbt_fraud
dbt build --profiles-dir . --project-dir .
cd ..
python -m src.train
python -m src.evaluate
```

## Monitoring
```bash
curl http://localhost:8000/metrics
curl http://localhost:8000/model/info
```

Les événements de prédiction sont écrits dans `data/monitoring/prediction_events.jsonl`.
