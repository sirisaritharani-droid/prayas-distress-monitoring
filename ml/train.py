import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from features import FEATURE_COLUMNS, calculate_baseline, extract_features_from_history
from generate_synthetic_data import generate_synthetic_cohort

def prepare_feature_dataset(df_raw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for user_id, group in df_raw.groupby("user_id"):
        records = group.sort_values("timestamp").to_dict("records")
        baseline = calculate_baseline(records, baseline_window=7)
        for i in range(1, len(records)):
            history_slice = records[:i+1]
            feats = extract_features_from_history(history_slice, baseline)
            if feats:
                feats["high_distress_flag"] = records[i]["high_distress_flag"]
                rows.append(feats)
    return pd.DataFrame(rows)

def train_and_evaluate_model():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic", "longitudinal_distress_dataset.csv")
    if not os.path.exists(csv_path):
        df_raw = generate_synthetic_cohort()
    else:
        df_raw = pd.read_csv(csv_path)

    df_feats = prepare_feature_dataset(df_raw)
    X = df_feats[FEATURE_COLUMNS]
    y = df_feats["high_distress_flag"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    base_rf = RandomForestClassifier(
        n_estimators=120,
        max_depth=6,
        min_samples_split=4,
        class_weight="balanced",
        random_state=42
    )
    
    calibrated_model = CalibratedClassifierCV(estimator=base_rf, method="sigmoid", cv=3)
    calibrated_model.fit(X_train, y_train)
    base_rf.fit(X_train, y_train)

    y_pred = calibrated_model.predict(X_test)
    y_prob = calibrated_model.predict_proba(X_test)[:, 1]

    metrics = {
        "dataset_records": int(len(df_feats)),
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "f1_score": float(f1_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "feature_importances": dict(zip(FEATURE_COLUMNS, base_rf.feature_importances_.tolist()))
    }

    model_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    os.makedirs(model_dir, exist_ok=True)
    model_artifact = {
        "model": calibrated_model,
        "base_rf": base_rf,
        "metrics": metrics,
        "feature_names": FEATURE_COLUMNS,
        "version": "1.0.0-sih2026",
        "description": "PRAYAS Longitudinal Random Forest with Sigmoid Calibration"
    }

    joblib_path = os.path.join(model_dir, "prayas_risk_model.joblib")
    joblib.dump(model_artifact, joblib_path)
    print(f"[PRAYAS ML] Model trained & saved to {joblib_path}")
    print(f"Recall: {metrics['recall']:.4f} | ROC-AUC: {metrics['roc_auc']:.4f} | Precision: {metrics['precision']:.4f}")
    return metrics

if __name__ == "__main__":
    train_and_evaluate_model()
