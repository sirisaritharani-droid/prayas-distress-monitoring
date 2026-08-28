import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

FEATURE_COLUMNS = [
    "current_mood",
    "current_stress",
    "current_anxiety",
    "current_sleep",
    "current_social",
    "current_safety",
    "current_energy",
    "mood_deviation",
    "stress_deviation",
    "anxiety_deviation",
    "sleep_deviation",
    "mood_3d_ma",
    "stress_3d_ma",
    "anxiety_3d_ma",
    "sleep_3d_ma",
    "mood_7d_ma",
    "stress_7d_ma",
    "mood_volatility_7d",
    "stress_volatility_7d",
    "consecutive_deterioration_count",
    "rate_of_change_mood_3d",
    "rate_of_change_stress_3d",
]

def calculate_baseline(checkins: List[Dict[str, Any]], baseline_window: int = 7) -> Dict[str, float]:
    if not checkins or len(checkins) < 3:
        return {
            "mood_baseline": 7.0,
            "stress_baseline": 3.0,
            "anxiety_baseline": 3.0,
            "sleep_baseline": 7.0,
            "social_baseline": 7.0,
            "safety_baseline": 7.0,
            "energy_baseline": 7.0,
            "is_preliminary": True
        }
    
    df = pd.DataFrame(checkins).sort_values("timestamp")
    baseline_slice = df.head(baseline_window)
    
    return {
        "mood_baseline": float(baseline_slice["mood"].mean()),
        "stress_baseline": float(baseline_slice["stress"].mean()),
        "anxiety_baseline": float(baseline_slice["anxiety"].mean()),
        "sleep_baseline": float(baseline_slice["sleep_hours"].mean()),
        "social_baseline": float(baseline_slice["social_connection"].mean()),
        "safety_baseline": float(baseline_slice["safety"].mean()),
        "energy_baseline": float(baseline_slice["energy"].mean()),
        "is_preliminary": False
    }

def extract_features_from_history(history: List[Dict[str, Any]], baseline: Dict[str, float]) -> Optional[Dict[str, float]]:
    if not history:
        return None

    df = pd.DataFrame(history).sort_values("timestamp").reset_index(drop=True)
    latest = df.iloc[-1]
    
    current_mood = float(latest["mood"])
    current_stress = float(latest["stress"])
    current_anxiety = float(latest["anxiety"])
    current_sleep = float(latest["sleep_hours"])
    current_social = float(latest["social_connection"])
    current_safety = float(latest["safety"])
    current_energy = float(latest["energy"])

    mood_dev = current_mood - baseline["mood_baseline"]
    stress_dev = current_stress - baseline["stress_baseline"]
    anxiety_dev = current_anxiety - baseline["anxiety_baseline"]
    sleep_dev = current_sleep - baseline["sleep_baseline"]

    last_3 = df.tail(3)
    last_7 = df.tail(7)

    mood_3d = float(last_3["mood"].mean())
    stress_3d = float(last_3["stress"].mean())
    anxiety_3d = float(last_3["anxiety"].mean())
    sleep_3d = float(last_3["sleep_hours"].mean())

    mood_7d = float(last_7["mood"].mean())
    stress_7d = float(last_7["stress"].mean())

    mood_vol_7d = float(last_7["mood"].std()) if len(last_7) > 1 else 0.0
    stress_vol_7d = float(last_7["stress"].std()) if len(last_7) > 1 else 0.0
    if np.isnan(mood_vol_7d): mood_vol_7d = 0.0
    if np.isnan(stress_vol_7d): stress_vol_7d = 0.0

    deterioration_count = 0
    if len(df) >= 2:
        for i in range(len(df) - 1, 0, -1):
            curr = df.iloc[i]
            prev = df.iloc[i - 1]
            if (curr["mood"] < prev["mood"]) or (curr["stress"] > prev["stress"]):
                deterioration_count += 1
            else:
                break

    if len(df) >= 3:
        roc_mood = float(df.iloc[-1]["mood"] - df.iloc[-3]["mood"]) / 2.0
        roc_stress = float(df.iloc[-1]["stress"] - df.iloc[-3]["stress"]) / 2.0
    elif len(df) == 2:
        roc_mood = float(df.iloc[-1]["mood"] - df.iloc[-2]["mood"])
        roc_stress = float(df.iloc[-1]["stress"] - df.iloc[-2]["stress"])
    else:
        roc_mood = 0.0
        roc_stress = 0.0

    return {
        "current_mood": current_mood,
        "current_stress": current_stress,
        "current_anxiety": current_anxiety,
        "current_sleep": current_sleep,
        "current_social": current_social,
        "current_safety": current_safety,
        "current_energy": current_energy,
        "mood_deviation": mood_dev,
        "stress_deviation": stress_dev,
        "anxiety_deviation": anxiety_dev,
        "sleep_deviation": sleep_dev,
        "mood_3d_ma": mood_3d,
        "stress_3d_ma": stress_3d,
        "anxiety_3d_ma": anxiety_3d,
        "sleep_3d_ma": sleep_3d,
        "mood_7d_ma": mood_7d,
        "stress_7d_ma": stress_7d,
        "mood_volatility_7d": mood_vol_7d,
        "stress_volatility_7d": stress_vol_7d,
        "consecutive_deterioration_count": float(deterioration_count),
        "rate_of_change_mood_3d": roc_mood,
        "rate_of_change_stress_3d": roc_stress,
    }
