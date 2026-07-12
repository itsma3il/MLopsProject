# restructure_project.sh
#!/bin/bash

echo "🔄 Restructuring Fraud Detection Project..."

# Create new directory structure
mkdir -p src/core/{data,models,pipeline,monitoring}
mkdir -p src/utils
mkdir -p src/api
mkdir -p infrastructure/{docker,kubernetes,terraform}
mkdir -p dbt_project/models/{staging,marts}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p docs/{api,guides,architecture/project}
mkdir -p figures/{exploration,model_evaluation,pipeline}
mkdir -p logs reports scripts
mkdir -p models/{registry,experiment_artifacts,production}

echo "✅ Directory structure created"

# Move core Python files
echo "📦 Moving core files..."

# Move data operations
mv src/dataset_loader.py src/core/data/ 2>/dev/null
mv src/preprocessing.py src/core/data/ 2>/dev/null
mv src/feature_engineering.py src/core/data/ 2>/dev/null
mv dataops/ingestion.py src/core/data/ 2>/dev/null

# Move model files
mv src/train.py src/core/models/ 2>/dev/null
mv src/predict.py src/core/models/ 2>/dev/null
mv src/evaluate.py src/core/models/ 2>/dev/null

# Move pipeline files
mv src/run_pipeline.py src/core/pipeline/ 2>/dev/null
mv src/pipeline_dashboard.py src/core/pipeline/ 2>/dev/null
mv src/pipeline_diagram.py src/core/pipeline/ 2>/dev/null

# Move monitoring
mv monitoring/metrics.py src/core/monitoring/ 2>/dev/null
mv monitoring/dashboard.py src/core/monitoring/ 2>/dev/null

# Move API
mv api/main.py src/api/ 2>/dev/null
mv api/model_loader.py src/api/ 2>/dev/null
mv api/schemas.py src/api/ 2>/dev/null
mv api/routes.py src/api/ 2>/dev/null

# Move utils
mv src/utils.py src/utils/ 2>/dev/null
mv src/data_contract.py src/utils/validation.py 2>/dev/null

# Move dbt
mv dbt_fraud/* dbt_project/ 2>/dev/null
rm -rf dbt_fraud 2>/dev/null

# Move tests
mv tests/test_*.py tests/unit/ 2>/dev/null
mv tests/test_api.py tests/integration/ 2>/dev/null

# Move docs
mv docs/*.md docs/guides/ 2>/dev/null
mv docs/architecture.md docs/architecture/ 2>/dev/null
mv docs/agile.md docs/project/ 2>/dev/null
mv docs/vision.md docs/project/ 2>/dev/null

# Move figures
mv figures/class_distribution.png figures/exploration/ 2>/dev/null
mv figures/*.png figures/model_evaluation/ 2>/dev/null

# Clean up old directories
rm -rf api dataops monitoring db __pycache__ 2>/dev/null

echo "✅ File migration complete"

# Create __init__.py files
touch src/core/__init__.py
touch src/core/data/__init__.py
touch src/core/models/__init__.py
touch src/core/pipeline/__init__.py
touch src/core/monitoring/__init__.py
touch src/api/__init__.py
touch src/utils/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py

echo "✅ __init__.py files created"

# Update imports in Python files
echo "📝 Updating imports..."

# Update import statements
find src -name "*.py" -exec sed -i 's/from src.dataset_loader/from src.core.data.dataset_loader/g' {} +
find src -name "*.py" -exec sed -i 's/from src.preprocessing/from src.core.data.preprocessing/g' {} +
find src -name "*.py" -exec sed -i 's/from src.feature_engineering/from src.core.data.feature_engineering/g' {} +
find src -name "*.py" -exec sed -i 's/from src.train/from src.core.models.train/g' {} +
find src -name "*.py" -exec sed -i 's/from src.predict/from src.core.models.predict/g' {} +
find src -name "*.py" -exec sed -i 's/from src.evaluate/from src.core.models.evaluate/g' {} +
find src -name "*.py" -exec sed -i 's/from src.utils/from src.utils/g' {} +
find src -name "*.py" -exec sed -i 's/from api/from src.api/g' {} +
find src -name "*.py" -exec sed -i 's/from monitoring/from src.core.monitoring/g' {} +

echo "✅ Import statements updated"

# Create setup.py
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="fraud-detection",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "xgboost",
        "mlflow",
        "fastapi",
        "uvicorn",
        "duckdb",
        "dbt-core",
        "dagster",
        "pytest",
        "loguru",
    ],
    entry_points={
        "console_scripts": [
            "train=src.core.models.train:main",
            "predict=src.core.models.predict:main",
            "run-pipeline=src.core.pipeline.run_pipeline:main",
            "serve-api=src.api.main:main",
        ],
    },
)
EOF

echo "✅ setup.py created"

# Create updated README
cat > README.md << 'EOF'
# Fraud Detection System

An end-to-end MLOps pipeline for credit card fraud detection.

## 📁 Project Structure
