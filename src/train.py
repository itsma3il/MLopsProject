"""Pipeline d'entrainement SANS data leakage.

Architecture:
    Load -> Clean -> Feature Engineering -> Split train/val/test -> Train (Scale+SMOTE+Model inside CV)
    -> Select on validation -> Refit final model on train+val -> Evaluate once on untouched test -> Save

SMOTE et Scaling sont INSIDE chaque fold de cross-validation via imblearn Pipeline.
Le test set reste INTOUCHE et n'est utilise qu'une seule fois, apres la selection.
"""

import json
import os
from typing import Dict

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from loguru import logger
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.preprocessing import RobustScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from config.settings import (
    CV_FOLDS,
    DATA_PROCESSED,
    FEATURE_COLUMNS_FILE,
    METRICS_FILE,
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_REGISTERED_MODEL,
    MLFLOW_TRACKING_URI,
    MODEL_FILENAME,
    MODELS_DIR,
    RANDOM_STATE,
    REFERENCE_STATS_FILE,
    SCALER_FILENAME,
    SMOTE_STRATEGY,
    TARGET_COLUMN,
    THRESHOLD_FILE,
    THRESHOLD_OPTIMIZATION_METRIC,
)
from src.dataset_loader import ensure_dataset
from src.evaluation_metrics import compute_imbalanced_metrics, optimize_threshold, save_threshold
from src.feature_engineering import add_features
from src.preprocessing import clean_data, load_raw_data, split_train_val_test


MODELS_CONFIG = {
    "logistic_regression": {
        "params": {"classifier__C": [0.01, 0.1, 1, 10]},
    },
    "decision_tree": {
        "params": {
            "classifier__max_depth": [3, 5, 7, 10],
            "classifier__min_samples_split": [10, 20, 50],
            "classifier__min_samples_leaf": [1, 2, 5],
        },
    },
    "random_forest": {
        "params": {
            "classifier__n_estimators": [200, 300],
            "classifier__max_depth": [8, 12, 16],
            "classifier__min_samples_leaf": [1, 2, 4],
        },
    },
    "xgboost": {
        "params": {
            "classifier__n_estimators": [150, 250, 350],
            "classifier__max_depth": [3, 4, 5, 6],
            "classifier__learning_rate": [0.01, 0.03, 0.05],
            "classifier__subsample": [0.7, 0.85, 1.0],
            "classifier__colsample_bytree": [0.7, 0.85, 1.0],
            "classifier__min_child_weight": [1, 5, 10],
            "classifier__gamma": [0, 1, 5],
            "classifier__reg_alpha": [0, 0.1, 1.0],
            "classifier__reg_lambda": [1.0, 3.0, 10.0],
        },
    },
}


def _make_classifier(name: str, scale_pos_weight: float):
    if name == "logistic_regression":
        return LogisticRegression(max_iter=5000, class_weight="balanced", random_state=RANDOM_STATE)
    if name == "decision_tree":
        return DecisionTreeClassifier(class_weight="balanced", random_state=RANDOM_STATE)
    if name == "random_forest":
        return RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1)
    if name == "xgboost":
        return XGBClassifier(
            eval_metric="aucpr",
            scale_pos_weight=scale_pos_weight,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
    raise ValueError(f"Unknown model: {name}")


def _make_pipeline(model_name: str, scale_pos_weight: float, use_smote: bool = True) -> ImbPipeline:
    steps = [("scaler", RobustScaler())]
    if use_smote:
        steps.append(("smote", SMOTE(random_state=RANDOM_STATE, sampling_strategy=SMOTE_STRATEGY)))
    steps.append(("classifier", _make_classifier(model_name, scale_pos_weight)))
    return ImbPipeline(steps)


def _train_model(model_name: str, X_train: pd.DataFrame, y_train: pd.Series, use_smote: bool = True):
    n_neg = (y_train == 0).sum()
    n_pos = max((y_train == 1).sum(), 1)
    scale_pos_weight = n_neg / n_pos
    pipeline = _make_pipeline(model_name, scale_pos_weight, use_smote=use_smote)
    params = MODELS_CONFIG[model_name]["params"]
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=params,
        n_iter=min(10, max(1, np.prod([len(v) for v in params.values()]))),
        cv=cv,
        scoring="f1",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=0,
    )
    search.fit(X_train, y_train)
    metrics = {
        "best_score": search.best_score_,
        "best_params": search.best_params_,
        "cv_f1": search.best_score_,
    }
    return search.best_estimator_, metrics


def train_single_model(model_name: str, X_train: pd.DataFrame, y_train: pd.Series, use_smote: bool = True):
    return _train_model(model_name, X_train, y_train, use_smote=use_smote)


def train_all_models(X_train: pd.DataFrame, y_train: pd.Series, use_smote: bool = True):
    results = {}
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for model_name in MODELS_CONFIG:
        estimator, metrics = _train_model(model_name, X_train, y_train, use_smote=use_smote)
        # Save each trained model for later per-model loading
        joblib.dump(estimator, MODELS_DIR / f"{model_name}.joblib")
        results[model_name] = (estimator, metrics)
    return results


def _build_models(scale_pos_weight: float) -> Dict:
    """Construit les pipelines imblearn avec Scale+SMOTE+Classifier."""
    return {
        "logistic_regression": {
            "pipeline": ImbPipeline([
                ("scaler", RobustScaler()),
                ("smote", SMOTE(random_state=RANDOM_STATE, sampling_strategy=SMOTE_STRATEGY)),
                ("classifier", LogisticRegression(
                    max_iter=5000, class_weight="balanced", random_state=RANDOM_STATE
                )),
            ]),
            "params": {"classifier__C": [0.01, 0.1, 1, 10]},
        },
        "decision_tree": {
            "pipeline": ImbPipeline([
                ("scaler", RobustScaler()),
                ("smote", SMOTE(random_state=RANDOM_STATE, sampling_strategy=SMOTE_STRATEGY)),
                ("classifier", DecisionTreeClassifier(
                    class_weight="balanced", random_state=RANDOM_STATE
                )),
            ]),
            "params": {
                "classifier__max_depth": [3, 5, 7, 10],
                "classifier__min_samples_split": [10, 20, 50],
                "classifier__min_samples_leaf": [1, 2, 5],
            },
        },
        "random_forest": {
            "pipeline": ImbPipeline([
                ("scaler", RobustScaler()),
                ("smote", SMOTE(random_state=RANDOM_STATE, sampling_strategy=SMOTE_STRATEGY)),
                ("classifier", RandomForestClassifier(
                    class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1
                )),
            ]),
            "params": {
                "classifier__n_estimators": [200, 300],
                "classifier__max_depth": [8, 12, 16],
                "classifier__min_samples_leaf": [1, 2, 4],
            },
        },
        "xgboost": {
            "pipeline": ImbPipeline([
                ("scaler", RobustScaler()),
                ("smote", SMOTE(random_state=RANDOM_STATE, sampling_strategy=SMOTE_STRATEGY)),
                ("classifier", XGBClassifier(
                    eval_metric="aucpr",
                    scale_pos_weight=scale_pos_weight,
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                )),
            ]),
            "params": {
                "classifier__n_estimators": [150, 250, 350],
                "classifier__max_depth": [3, 4, 5, 6],
                "classifier__learning_rate": [0.01, 0.03, 0.05],
                "classifier__subsample": [0.7, 0.85, 1.0],
                "classifier__colsample_bytree": [0.7, 0.85, 1.0],
                "classifier__min_child_weight": [1, 5, 10],
                "classifier__gamma": [0, 1, 5],
                "classifier__reg_alpha": [0, 0.1, 1.0],
                "classifier__reg_lambda": [1.0, 3.0, 10.0],
            },
        },
    }


def _evaluate_estimator(model: object, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
    """Compute leak-free imbalanced classification metrics for a fitted estimator."""
    y_proba = model.predict_proba(X)[:, 1]
    return compute_imbalanced_metrics(y, y_proba)


def _sort_key(item):
    metrics = item[1]
    return (metrics["val_pr_auc"], metrics["val_f1"], metrics["cv_f1"])


def _write_reference_stats(X_train: pd.DataFrame, y_train: pd.Series) -> None:
    """Persist compact feature statistics for simple production drift checks."""
    numeric_stats = X_train.describe().loc[["mean", "std", "min", "max"]].to_dict()
    stats = {
        "row_count": int(len(X_train)),
        "target_rate": float(y_train.mean()),
        "features": numeric_stats,
    }
    with open(MODELS_DIR / REFERENCE_STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)


def _log_mlflow_run(
    best_pipeline: object,
    best_name: str,
    feature_columns: list[str],
    test_metrics: Dict,
    model_params: Dict,
) -> None:
    """Log experiment metadata, metrics, and artifacts to MLflow if available."""
    try:
        import mlflow
        import mlflow.sklearn
        from mlflow.models import infer_signature
    except ImportError:
        logger.warning("MLflow is not installed; skipping experiment tracking.")
        return

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    with mlflow.start_run(run_name=f"{best_name}-final") as run:
        mlflow.log_param("best_model", best_name)
        mlflow.log_param("random_state", RANDOM_STATE)
        mlflow.log_param("smote_strategy", SMOTE_STRATEGY)
        for key, value in model_params.items():
            mlflow.log_param(key, value)
        for key, value in test_metrics.items():
            if isinstance(value, (int, float)):
                mlflow.log_metric(key, float(value))
        mlflow.log_artifact(str(MODELS_DIR / MODEL_FILENAME))
        mlflow.log_artifact(str(MODELS_DIR / FEATURE_COLUMNS_FILE))
        mlflow.log_artifact(str(MODELS_DIR / METRICS_FILE))
        threshold_file = MODELS_DIR / THRESHOLD_FILE
        if threshold_file.exists():
            mlflow.log_artifact(str(threshold_file))
        reference_stats = MODELS_DIR / REFERENCE_STATS_FILE
        if reference_stats.exists():
            mlflow.log_artifact(str(reference_stats))

        input_example = pd.DataFrame([{column: 0.0 for column in feature_columns}])
        signature = infer_signature(input_example, best_pipeline.predict(input_example))
        registered_name = os.getenv("MLFLOW_REGISTER_MODEL", "true").lower() != "false"
        mlflow.sklearn.log_model(
            sk_model=best_pipeline,
            artifact_path="model",
            signature=signature,
            input_example=input_example,
            registered_model_name=MLFLOW_REGISTERED_MODEL if registered_name else None,
        )
        logger.info(f"MLflow run logged: {run.info.run_id}")


def run_training_pipeline() -> Dict:
    """Execute le pipeline complet sans data leakage."""
    logger.info("=" * 60)
    logger.info("PIPELINE D'ENTRAINEMENT (leakage-free)")
    logger.info("=" * 60)

    # 1. Ensure dataset
    ensure_dataset()

    # 2. Load & Clean
    df = load_raw_data()
    df = clean_data(df)

    # 3. Feature Engineering (row-wise, sans target)
    df = add_features(df)

    # 4. Split propre train / validation / test
    X_train, X_val, X_test, y_train, y_val, y_test = split_train_val_test(df)
    feature_columns = list(X_train.columns)

    X_train_val = pd.concat([X_train, X_val], axis=0)
    y_train_val = pd.concat([y_train, y_val], axis=0)

    # Compute imbalance ratio for XGBoost scale_pos_weight
    n_neg = (y_train == 0).sum()
    n_pos = (y_train == 1).sum()
    scale_pos_weight = n_neg / n_pos
    logger.info(f"Imbalance ratio: {n_neg}:{n_pos} (scale_pos_weight={scale_pos_weight:.1f})")

    # 5. Build models with imblearn pipelines (Scale+SMOTE INSIDE CV)
    models_config = _build_models(scale_pos_weight)
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    results = {}
    for name, cfg in models_config.items():
        logger.info(f"Training: {name}")
        search = RandomizedSearchCV(
            estimator=cfg["pipeline"],
            param_distributions=cfg["params"],
            n_iter=min(10, max(1, np.prod([len(v) for v in cfg["params"].values()]))),
            cv=cv,
            scoring="f1",
            random_state=RANDOM_STATE,
            n_jobs=-1,
            verbose=0,
        )
        search.fit(X_train, y_train)
        val_metrics = _evaluate_estimator(search.best_estimator_, X_val, y_val)
        results[name] = {
            "estimator": search.best_estimator_,
            "cv_f1": search.best_score_,
            "params": search.best_params_,
            "val_metrics": val_metrics,
            "val_f1": val_metrics["f1_score"],
            "val_pr_auc": val_metrics["pr_auc"],
        }
        logger.info(
            f"  {name}: CV F1={search.best_score_:.4f} | "
            f"VAL F1={val_metrics['f1_score']:.4f} | VAL PR-AUC={val_metrics['pr_auc']:.4f}"
        )

    # 6. Select best model on validation only
    best_name = max(results.items(), key=_sort_key)[0]
    best_pipeline = results[best_name]["estimator"]
    logger.info(
        f"Meilleur modele: {best_name} "
        f"(VAL PR-AUC={results[best_name]['val_pr_auc']:.4f}, VAL F1={results[best_name]['val_f1']:.4f})"
    )

    # Optimize the operational threshold on validation only.
    val_proba = best_pipeline.predict_proba(X_val)[:, 1]
    decision_threshold, threshold_metrics = optimize_threshold(
        y_val,
        val_proba,
        metric=THRESHOLD_OPTIMIZATION_METRIC,
    )
    logger.info(
        f"Decision threshold selected on validation: {decision_threshold:.4f} "
        f"({THRESHOLD_OPTIMIZATION_METRIC}={threshold_metrics[THRESHOLD_OPTIMIZATION_METRIC]:.4f}, "
        f"recall={threshold_metrics['recall']:.4f}, precision={threshold_metrics['precision']:.4f})"
    )

    # Refit final pipeline on train + validation before the untouched test evaluation
    best_pipeline.fit(X_train_val, y_train_val)

    # 7. Evaluate on UNTOUCHED test set (original distribution, no SMOTE)
    # The pipeline handles scaling internally
    test_proba = best_pipeline.predict_proba(X_test)[:, 1]
    test_metrics = compute_imbalanced_metrics(y_test, test_proba, threshold=decision_threshold)
    test_metrics["best_model"] = best_name
    test_metrics["cv_f1"] = results[best_name]["cv_f1"]
    test_metrics["val_f1"] = results[best_name]["val_f1"]
    test_metrics["val_pr_auc"] = results[best_name]["val_pr_auc"]
    test_metrics["threshold_validation_metrics"] = threshold_metrics
    test_metrics["metric_note"] = (
        "Accuracy is reported for completeness only. Fraud is a rare-event problem; "
        "use PR-AUC, recall, precision, F1, MCC and balanced_accuracy for model selection."
    )

    logger.info("=== TEST SET EVALUATION (untouched) ===")
    for k, v in test_metrics.items():
        if k not in ("confusion_matrix", "best_model", "threshold_validation_metrics", "metric_note"):
            logger.info(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
    logger.info(
        f"  Confusion Matrix: TN={test_metrics['tn']} FP={test_metrics['fp']} "
        f"FN={test_metrics['fn']} TP={test_metrics['tp']}"
    )

    # 8. Save artifacts
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    # Save the full pipeline (scaler + classifier, SMOTE excluded at predict time)
    joblib.dump(best_pipeline, MODELS_DIR / MODEL_FILENAME)

    # Save scaler separately for predict.py compatibility
    scaler = best_pipeline.named_steps["scaler"]
    joblib.dump(scaler, MODELS_DIR / SCALER_FILENAME)

    with open(MODELS_DIR / FEATURE_COLUMNS_FILE, "w") as f:
        json.dump(feature_columns, f)

    with open(MODELS_DIR / METRICS_FILE, "w") as f:
        json.dump(test_metrics, f, indent=2)

    save_threshold(decision_threshold, threshold_metrics)
    _write_reference_stats(X_train, y_train)

    # Save test data for standalone evaluation
    X_train.to_csv(DATA_PROCESSED / "X_train.csv", index=False)
    y_train.to_csv(DATA_PROCESSED / "y_train.csv", index=False)
    X_val.to_csv(DATA_PROCESSED / "X_val.csv", index=False)
    y_val.to_csv(DATA_PROCESSED / "y_val.csv", index=False)
    X_test.to_csv(DATA_PROCESSED / "X_test.csv", index=False)
    y_test.to_csv(DATA_PROCESSED / "y_test.csv", index=False)

    _log_mlflow_run(
        best_pipeline=best_pipeline,
        best_name=best_name,
        feature_columns=feature_columns,
        test_metrics=test_metrics,
        model_params=results[best_name]["params"],
    )

    logger.info(f"Artefacts sauvegardes dans: {MODELS_DIR}")
    return {"best_model": best_name, "results": results, "metrics": test_metrics}


if __name__ == "__main__":
    run_training_pipeline()
