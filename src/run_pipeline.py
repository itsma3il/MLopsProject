# run_pipeline.py
"""
Complete pipeline runner for Fraud Detection System.
Usage: python run_pipeline.py [--step STEP] [--all]
"""

import subprocess
import sys
from pathlib import Path
from loguru import logger
import argparse
import time
from typing import Dict, List, Optional


class PipelineRunner:
    """Orchestrates the entire ML pipeline."""
    
    def __init__(self):
        self.steps = {
            "ingest": self.run_ingestion,
            "dbt": self.run_dbt,
            "preprocess": self.run_preprocessing,
            "features": self.run_feature_engineering,
            "train": self.run_training,
            "evaluate": self.run_evaluation,
            "predict": self.run_prediction,
            "api": self.run_api,
            "monitor": self.run_monitoring
        }
        self.results: Dict[str, bool] = {}
        self.start_time = time.time()
    
    def run_command(self, cmd: str, description: str) -> bool:
        """Run a shell command and log results."""
        logger.info(f"🚀 Running: {description}")
        logger.info(f"   Command: {cmd}")
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            logger.success(f"✅ {description} completed successfully")
            logger.debug(f"Output: {result.stdout[:200]}...")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ {description} failed")
            logger.error(f"Error: {e.stderr}")
            return False
    
    def run_ingestion(self) -> bool:
        """Run data ingestion."""
        # Check if data exists
        if Path("data/raw/creditcard.csv").exists():
            logger.info("Dataset already exists, skipping download")
            return True
        return self.run_command(
            "python -m src.dataset_loader",
            "Data Loading from Kaggle"
        )
    
    def run_ingestion_to_db(self) -> bool:
        """Ingest data into DuckDB."""
        return self.run_command(
            "python -m dataops.ingestion",
            "Data Ingestion to DuckDB"
        )
    
    def run_dbt(self) -> bool:
        """Run dbt transformations."""
        return self.run_command(
            "cd dbt_fraud && dbt run",
            "dbt Transformations"
        )
    
    def run_preprocessing(self) -> bool:
        """Run preprocessing."""
        return self.run_command(
            "python -m src.preprocessing",
            "Data Preprocessing"
        )
    
    def run_feature_engineering(self) -> bool:
        """Run feature engineering."""
        return self.run_command(
            "python -m src.feature_engineering",
            "Feature Engineering"
        )
    
    def run_training(self) -> bool:
        """Run model training."""
        return self.run_command(
            "python -m src.train",
            "Model Training"
        )
    
    def run_evaluation(self) -> bool:
        """Run model evaluation."""
        return self.run_command(
            "python -m src.evaluate",
            "Model Evaluation"
        )
    
    def run_prediction(self) -> bool:
        """Run predictions."""
        return self.run_command(
            "python -m src.predict",
            "Generate Predictions"
        )
    
    def run_api(self) -> bool:
        """Start the API server."""
        return self.run_command(
            "python -m api.main &",
            "API Server (background)"
        )
    
    def run_monitoring(self) -> bool:
        """Run monitoring."""
        return self.run_command(
            "python -m monitoring.metrics",
            "System Monitoring"
        )
    
    def run_full_pipeline(self) -> bool:
        """Run all steps in order."""
        logger.info("=" * 60)
        logger.info("🚀 Starting Full Pipeline Execution")
        logger.info("=" * 60)
        
        steps_order = [
            ("ingest", "Data Loading"),
            ("db_ingest", "Database Ingestion"),
            ("dbt", "dbt Transformations"),
            ("preprocess", "Preprocessing"),
            ("features", "Feature Engineering"),
            ("train", "Model Training"),
            ("evaluate", "Model Evaluation"),
            ("predict", "Predictions")
        ]
        
        for step_name, description in steps_order:
            logger.info("\n" + "=" * 60)
            logger.info(f"📌 Step: {description}")
            logger.info("=" * 60)
            
            if step_name == "ingest":
                success = self.run_ingestion()
            elif step_name == "db_ingest":
                success = self.run_ingestion_to_db()
            else:
                success = self.steps[step_name]()
            
            self.results[step_name] = success
            
            if not success:
                logger.error(f"❌ Pipeline failed at step: {description}")
                return False
        
        elapsed = time.time() - self.start_time
        logger.success(f"✅ Full pipeline completed in {elapsed:.2f} seconds")
        return True
    
    def run_single_step(self, step: str) -> bool:
        """Run a single pipeline step."""
        if step not in self.steps:
            logger.error(f"Unknown step: {step}")
            logger.info(f"Available steps: {', '.join(self.steps.keys())}")
            return False
        
        logger.info(f"Running single step: {step}")
        success = self.steps[step]()
        
        if success:
            logger.success(f"✅ Step '{step}' completed successfully")
        else:
            logger.error(f"❌ Step '{step}' failed")
        
        return success


def show_pipeline_status():
    """Show current pipeline status."""
    logger.info("\n📊 Pipeline Status:")
    logger.info("-" * 40)
    
    checks = {
        "Dataset downloaded": Path("data/raw/creditcard.csv").exists(),
        "DuckDB created": Path("data/warehouse/fraud.duckdb").exists(),
        "dbt models built": Path("dbt_fraud/target/manifest.json").exists(),
        "Features saved": Path("models/feature_columns.json").exists(),
        "Metrics saved": Path("models/metrics.json").exists(),
    }
    
    for check, exists in checks.items():
        status = "✅" if exists else "❌"
        logger.info(f"  {status} {check}")
    
    logger.info("-" * 40)


def create_pipeline_report():
    """Generate pipeline summary for academic report."""
    logger.info("\n" + "=" * 60)
    logger.info("📋 Pipeline Summary Report")
    logger.info("=" * 60)
    
    # Data statistics
    import pandas as pd
    if Path("data/raw/creditcard.csv").exists():
        df = pd.read_csv("data/raw/creditcard.csv")
        logger.info(f"📊 Dataset Statistics:")
        logger.info(f"   Total samples: {len(df):,}")
        logger.info(f"   Features: {len(df.columns) - 1}")
        logger.info(f"   Fraud cases: {df['Class'].sum():,}")
        logger.info(f"   Fraud rate: {df['Class'].mean()*100:.4f}%")
    
    # Model metrics
    if Path("models/metrics.json").exists():
        import json
        with open("models/metrics.json", 'r') as f:
            metrics = json.load(f)
        logger.info(f"\n🎯 Model Performance:")
        for name, value in metrics.items():
            if isinstance(value, (int, float)):
                logger.info(f"   {name}: {value:.4f}")
    
    # Database status
    if Path("data/warehouse/fraud.duckdb").exists():
        import duckdb
        try:
            with duckdb.connect("data/warehouse/fraud.duckdb") as con:
                tables = con.execute("SHOW TABLES").fetchall()
                logger.info(f"\n💾 Database Tables:")
                for table in tables:
                    logger.info(f"   - {table[0]}")
        except:
            pass
    
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ML Pipeline")
    parser.add_argument(
        "--step", 
        choices=["ingest", "dbt", "preprocess", "features", "train", 
                "evaluate", "predict", "api", "monitor"],
        help="Run a specific pipeline step"
    )
    parser.add_argument(
        "--all", 
        action="store_true",
        help="Run the complete pipeline"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show pipeline status"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate pipeline report"
    )
    
    args = parser.parse_args()
    
    runner = PipelineRunner()
    
    if args.status:
        show_pipeline_status()
    elif args.report:
        create_pipeline_report()
    elif args.step:
        runner.run_single_step(args.step)
    elif args.all:
        runner.run_full_pipeline()
    else:
        # Default: show help
        parser.print_help()