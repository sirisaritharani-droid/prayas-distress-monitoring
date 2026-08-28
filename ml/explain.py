import numpy as np
import pandas as pd
from typing import Dict, Any, List
from predict import load_prayas_model
from features import FEATURE_COLUMNS

def explain_prediction(features: Dict[str, float]) -> List[Dict[str, Any]]:
    artifact = load_prayas_model()
    base_rf = artifact["base_rf"]
    importances = dict(zip(FEATURE_COLUMNS, base_rf.feature_importances_))

    explanations = []
    mapping = {
        "stress_deviation": ("Stress level significantly elevated compared to personal baseline", 1.8),
        "sleep_deviation": ("Substantial drop in nightly sleep duration", 1.6),
        "mood_deviation": ("Marked decline in mood score from baseline", 1.5),
        "anxiety_deviation": ("Heightened anxiety relative to usual state", 1.4),
        "consecutive_deterioration_count": ("Consecutive multi-day downward trajectory detected", 1.3),
        "rate_of_change_stress_3d": ("Rapid escalation in stress across recent check-ins", 1.2),
        "current_safety": ("Reduced feeling of personal safety or physical security", 1.1),
        "current_social": ("Decreased social connection or emerging isolation", 1.0)
    }

    for feat_key, (human_desc, weight_mult) in mapping.items():
        val = features.get(feat_key, 0.0)
        base_imp = importances.get(feat_key, 0.05)
        
        is_contributing = False
        impact_score = 0.0

        if "deviation" in feat_key:
            if "stress" in feat_key or "anxiety" in feat_key:
                if val > 1.0:
                    is_contributing = True
                    impact_score = float(val * base_imp * weight_mult * 10)
            elif "mood" in feat_key or "sleep" in feat_key:
                if val < -1.0:
                    is_contributing = True
                    impact_score = float(abs(val) * base_imp * weight_mult * 10)
        elif feat_key == "consecutive_deterioration_count" and val >= 2:
            is_contributing = True
            impact_score = float(val * base_imp * weight_mult * 8)
        elif feat_key == "rate_of_change_stress_3d" and val > 0.5:
            is_contributing = True
            impact_score = float(val * base_imp * weight_mult * 8)
        elif feat_key in ["current_safety", "current_social"] and val <= 4.0:
            is_contributing = True
            impact_score = float((6.0 - val) * base_imp * weight_mult * 5)

        if is_contributing:
            explanations.append({
                "feature": feat_key,
                "description": human_desc,
                "importance_score": round(min(impact_score, 10.0), 2),
                "direction": "RISK_INCREASING"
            })

    explanations.sort(key=lambda x: x["importance_score"], reverse=True)
    
    if not explanations:
        explanations.append({
            "feature": "stable_pattern",
            "description": "Check-in values reflect your usual personal baseline pattern",
            "importance_score": 1.0,
            "direction": "STABLE"
        })

    return explanations
