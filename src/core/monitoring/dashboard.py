# monitoring/dashboard.py
"""
FastAPI endpoint for pipeline monitoring.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pathlib import Path
import json
import pandas as pd
import duckdb
from typing import Dict, Any
from datetime import datetime

app = FastAPI(title="Pipeline Monitor", version="1.0.0")

@app.get("/")
async def root():
    """Root endpoint with pipeline status."""
    return {
        "service": "Pipeline Monitor",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
async def pipeline_status() -> Dict[str, Any]:
    """Get full pipeline status."""
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "components": {
            "data": check_data_status(),
            "database": check_database_status(),
            "dbt": check_dbt_status(),
            "model": check_model_status(),
            "api": check_api_status()
        },
        "metrics": get_model_metrics(),
        "data_stats": get_data_stats()
    }
    
    return status

def check_data_status() -> Dict[str, Any]:
    """Check data layer status."""
    raw_path = Path("data/raw/creditcard.csv")
    return {
        "loaded": raw_path.exists(),
        "size_mb": raw_path.stat().st_size / (1024*1024) if raw_path.exists() else 0,
        "path": str(raw_path)
    }

def check_database_status() -> Dict[str, Any]:
    """Check database status."""
    db_path = Path("data/warehouse/fraud.duckdb")
    status = {
        "exists": db_path.exists(),
        "size_mb": db_path.stat().st_size / (1024*1024) if db_path.exists() else 0
    }
    
    if db_path.exists():
        try:
            with duckdb.connect(str(db_path)) as con:
                tables = con.execute("SHOW TABLES").fetchall()
                status["tables"] = [t[0] for t in tables]
                
                for table in tables:
                    count = con.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
                    status[f"{table[0]}_rows"] = count
        except:
            pass
    
    return status

def check_dbt_status() -> Dict[str, Any]:
    """Check dbt status."""
    manifest_path = Path("dbt_fraud/target/manifest.json")
    return {
        "manifest_exists": manifest_path.exists(),
        "models_built": manifest_path.exists()
    }

def check_model_status() -> Dict[str, Any]:
    """Check model status."""
    return {
        "metrics_exists": Path("models/metrics.json").exists(),
        "features_exists": Path("models/feature_columns.json").exists()
    }

def check_api_status() -> Dict[str, Any]:
    """Check API status."""
    api_path = Path("api/main.py")
    return {
        "api_exists": api_path.exists(),
        "service": "FastAPI",
        "endpoint": "/predict"
    }

def get_model_metrics() -> Dict[str, float]:
    """Get model performance metrics."""
    metrics_path = Path("models/metrics.json")
    if metrics_path.exists():
        with open(metrics_path, 'r') as f:
            return json.load(f)
    return {}

def get_data_stats() -> Dict[str, Any]:
    """Get data statistics."""
    raw_path = Path("data/raw/creditcard.csv")
    if raw_path.exists():
        df = pd.read_csv(raw_path)
        return {
            "total_samples": len(df),
            "features": len(df.columns) - 1,
            "fraud_count": int(df['Class'].sum()),
            "fraud_rate": float(df['Class'].mean()),
            "memory_mb": df.memory_usage(deep=True).sum() / (1024*1024)
        }
    return {}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """HTML dashboard."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pipeline Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: auto; }
            .card { background: white; padding: 20px; margin: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .status-ok { color: green; }
            .status-warning { color: orange; }
            .status-error { color: red; }
            h1 { color: #2C3E50; }
            .metric { font-size: 24px; font-weight: bold; }
            .label { color: #666; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Pipeline Dashboard</h1>
            <div id="status" class="grid">
                <!-- Will be filled by JavaScript -->
            </div>
        </div>
        
        <script>
            async function loadStatus() {
                const response = await fetch('/status');
                const data = await response.json();
                
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = '';
                
                // Data Card
                const dataCard = createCard('📊 Data', data.components.data);
                statusDiv.appendChild(dataCard);
                
                // Database Card
                const dbCard = createCard('💾 Database', data.components.database);
                statusDiv.appendChild(dbCard);
                
                // Model Card
                const modelCard = createCard('🎯 Model', data.components.model);
                statusDiv.appendChild(modelCard);
                
                // Metrics Card
                const metricsCard = createMetricsCard('📈 Metrics', data.metrics);
                statusDiv.appendChild(metricsCard);
            }
            
            function createCard(title, data) {
                const div = document.createElement('div');
                div.className = 'card';
                
                let html = `<h3>${title}</h3>`;
                for (const [key, value] of Object.entries(data)) {
                    const status = value ? '✅' : '❌';
                    html += `<div>${status} ${key}: ${value}</div>`;
                }
                div.innerHTML = html;
                return div;
            }
            
            function createMetricsCard(title, metrics) {
                const div = document.createElement('div');
                div.className = 'card';
                
                let html = `<h3>${title}</h3>`;
                for (const [key, value] of Object.entries(metrics)) {
                    const color = value > 0.8 ? 'green' : value > 0.6 ? 'orange' : 'red';
                    html += `<div style="color: ${color}">${key}: ${value.toFixed(4)}</div>`;
                }
                div.innerHTML = html;
                return div;
            }
            
            loadStatus();
            setInterval(loadStatus, 30000); // Refresh every 30 seconds
        </script>
    </body>
    </html>
    """
    return html