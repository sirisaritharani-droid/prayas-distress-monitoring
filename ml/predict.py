import os
import joblib
import pandas as pd
from typing import Dict, Any, List
from features import FEATURE_COLUMNS, calculate_baseline, extract_features_from_history

MODEL_CACHE = None

def load_prayas_model():
    global MODEL_CACHE
    if MODEL_CACHE is None:
        model_path = os.getenv("MODEL_PATH", os.path.join(os.path.dirname(__file__), "..", "models", "prayas_risk_model.joblib"))
        if not os.path.exists(model_path):
            from train import train_and_evaluate_model
            train_and_evaluate_model()
        MODEL_CACHE = joblib.load(model_path)
    return MODEL_CACHE

def evaluate_distress_risk(history: List[Dict[str, Any]], custom_baseline: Dict[str, float] = None) -> Dict[str, Any]:
    if not history or len(history) < 1:
        return {
            "status": "insufficient_data",
            "message": "Not enough data to establish a reliable personal baseline.",
            "risk_probability": 0.0,
            "risk_level": "UNKNOWN",
            "confidence": 0.0,
            "trend_direction": "UNKNOWN",
            "baseline": custom_baseline or {}
        }

    baseline = custom_baseline or calculate_baseline(history, baseline_window=7)
    features = extract_features_from_history(history, baseline)
    
    artifact = load_prayas_model()
    model = artifact["model"]

    feat_df = pd.DataFrame([features])[FEATURE_COLUMNS]
    prob = float(model.predict_proba(feat_df)[0][1])

    if prob >= 0.65:
        risk_level = "HIGH"
    elif prob >= 0.35:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    if features["rate_of_change_stress_3d"] > 0.4 or features["rate_of_change_mood_3d"] < -0.4:
        trend = "INCREASING"
    elif features["rate_of_change_stress_3d"] < -0.4 or features["rate_of_change_mood_3d"] > 0.4:
        trend = "IMPROVING"
    else:
        trend = "STABLE"

    confidence = round(float(0.70 + (abs(prob - 0.5) * 0.55)), 2)

    return {
        "status": "success",
        "risk_probability": round(prob, 3),
        "risk_percentage": int(round(prob * 100)),
        "risk_level": risk_level,
        "confidence": confidence,
        "trend_direction": trend,
        "baseline": baseline,
        "features": features,
        "action_recommendation": "Immediate human assessment recommended." if risk_level == "HIGH" else (
            "Support review recommended." if risk_level == "MODERATE" else "Routine self-monitoring."
        )
    }
