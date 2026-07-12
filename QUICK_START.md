# Complete Pipeline Commands Guide

## 1. Setup and Installation

```bash
# Clone and navigate to project
cd fraud-detection

# Install dependencies
pip install -r requirements.txt

# Install additional packages for pipeline
pip install graphviz streamlit uvicorn fastapi duckdb dbt-core

# Create necessary directories
mkdir -p logs reports figures models/cache
```

## 2. Data Pipeline Commands

### A. Data Ingestion Pipeline

```bash
# Option 1: Download dataset from Kaggle
python -m src.dataset_loader

# Option 2: Ingest data into DuckDB (using our new scripts)
python -m dataops.ingestion

# Option 3: Run the full data pipeline script
python run_pipeline.py --step ingest
```

### B. Database Pipeline

```bash
# Check database status
python run_pipeline.py --status

# Query database directly
duckdb data/warehouse/fraud.duckdb

# Inside DuckDB console:
# SHOW TABLES;
# SELECT COUNT(*) FROM raw.creditcard_transactions;
# SELECT * FROM raw.creditcard_transactions LIMIT 5;
```

### C. dbt Transformations

```bash
# Navigate to dbt project
cd dbt_fraud/

# Run dbt models
dbt run

# Run specific model
dbt run --models stg_transactions

# Test dbt models
dbt test

# Generate documentation
dbt docs generate
dbt docs serve

# Back to project root
cd ..
```

## 3. ML Pipeline Commands

### A. Preprocessing and Feature Engineering

```bash
# Run preprocessing
python -m src.preprocessing

# Run feature engineering
python -m src.feature_engineering

# Or run all steps
python run_pipeline.py --all
```

### B. Model Training

```bash
# Train model
python -m src.train

# Train with specific config (if available)
python -m src.train --config config/training_config.yaml

# Quick training with pipeline
python run_pipeline.py --step train
```

### C. Model Evaluation

```bash
# Evaluate model
python -m src.evaluate

# Generate predictions
python -m src.predict

# Get model metrics
python run_pipeline.py --report
```

## 4. API Service Commands

### A. Start API Server

```bash
# Start FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python module
python -m api.main

# Run in background
nohup uvicorn api.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
```

### B. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Check API status
curl http://localhost:8000/status

# Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "time": 100,
      "amount": 50.0,
      "v1": -1.2,
      "v2": 0.5,
      "v3": 1.3,
      "v4": -0.8
    }
  }'

# Test with sample data
curl -X POST http://localhost:8000/predict_batch \
  -H "Content-Type: application/json" \
  -d @samples/creditcard_sample.csv
```

## 5. Monitoring and Dashboard Commands

### A. Pipeline Monitor Dashboard

```bash
# Start monitoring dashboard
uvicorn monitoring.dashboard:app --reload --port 8001

# Access dashboard
# Open browser: http://localhost:8001/dashboard

# Check pipeline status via API
curl http://localhost:8001/status
```

### B. Streamlit Dashboard

```bash
# Create and run Streamlit dashboard
streamlit run pipeline_dashboard.py

# Open browser: http://localhost:8501
```

### C. MLflow Tracking

```bash
# Start MLflow UI
mlflow ui --backend-store-uri ./mlruns --port 5000

# Open browser: http://localhost:5000
```

## 6. Pipeline Orchestration

### A. Run Complete Pipeline

```bash
# Run full pipeline (all steps)
python run_pipeline.py --all

# Run specific step
python run_pipeline.py --step train
python run_pipeline.py --step evaluate
python run_pipeline.py --step api

# Show pipeline status
python run_pipeline.py --status

# Generate report
python run_pipeline.py --report
```

### B. Using Shell Script

```bash
# Make script executable
chmod +x run_pipeline.sh

# Run pipeline
./run_pipeline.sh

# Run with specific steps
./run_pipeline.sh --step train
```

### C. Dagster Pipeline (if configured)

```bash
# Start Dagster UI
cd dagster_project/
dagster dev -f definitions.py

# Open browser: http://localhost:3000
```

## 7. Docker Commands

### A. Build and Run with Docker

```bash
# Build Docker image
docker build -t fraud-detection .

# Run container
docker run -p 8000:8000 -p 8001:8001 fraud-detection

# Run with Docker Compose
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f
```

### B. Docker Commands

```bash
# Build image
docker build -t fraud-detection:latest .

# Run with volume mounts for development
docker run -v $(pwd):/app -p 8000:8000 fraud-detection

# Run in background
docker run -d --name fraud-api -p 8000:8000 fraud-detection

# Execute inside container
docker exec -it fraud-api /bin/bash

# Clean up
docker stop fraud-api
docker rm fraud-api
```

## 8. Utility Commands

### A. Pipeline Diagram Generation

```bash
# Generate pipeline diagram
python pipeline_diagram.py

# Output: pipeline_diagram.png
```

### B. Data Validation

```bash
# Validate data contract
python -c "from src.data_contract import assert_creditcard_contract; import pandas as pd; df = pd.read_csv('data/raw/creditcard.csv'); assert_creditcard_contract(df); print('✅ Data valid')"

# Check data quality
python -m monitoring.metrics
```

### C. Logs and Reports

```bash
# View logs
tail -f logs/pipeline.log

# Generate final report
python -m docs.generate_report

# Clean cache and temp files
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

## 9. Testing Commands

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_data_contract.py

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run API tests
pytest tests/test_api.py

# Run in verbose mode
pytest -v tests/
```

## 12. Debugging Commands

```bash
# Debug a specific step
python -m src.train --debug

# Run with more logging
LOG_LEVEL=DEBUG python -m src.train

# Check database connection
duckdb data/warehouse/fraud.duckdb -c "SELECT 1"

# Test model loading
python -c "from api.model_loader import load_model; model = load_model(); print('✅ Model loaded')"

# Check data quality
python -m monitoring.metrics --check-quality

# View recent errors
tail -50 logs/pipeline.log | grep -i error
```
