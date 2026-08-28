import pytest
from ml.features import calculate_baseline, extract_features_from_history

def test_baseline_calculation():
    checkins = [
        {"timestamp": "2026-08-01", "mood": 7.0, "stress": 3.0, "anxiety": 3.0, "sleep_hours": 7.0, "social_connection": 7.0, "safety": 7.0, "energy": 7.0},
        {"timestamp": "2026-08-02", "mood": 8.0, "stress": 2.0, "anxiety": 2.0, "sleep_hours": 8.0, "social_connection": 8.0, "safety": 8.0, "energy": 8.0},
        {"timestamp": "2026-08-03", "mood": 6.0, "stress": 4.0, "anxiety": 4.0, "sleep_hours": 6.0, "social_connection": 6.0, "safety": 6.0, "energy": 6.0},
    ]
    b = calculate_baseline(checkins)
    assert b["mood_baseline"] == 7.0
    assert b["stress_baseline"] == 3.0
    assert b["is_preliminary"] is False

def test_feature_deviations():
    history = [
        {"timestamp": "2026-08-01", "mood": 7.0, "stress": 3.0, "anxiety": 3.0, "sleep_hours": 7.0, "social_connection": 7.0, "safety": 7.0, "energy": 7.0},
        {"timestamp": "2026-08-02", "mood": 3.0, "stress": 8.0, "anxiety": 7.0, "sleep_hours": 4.0, "social_connection": 4.0, "safety": 4.0, "energy": 4.0}
    ]
    baseline = {"mood_baseline": 7.0, "stress_baseline": 3.0, "anxiety_baseline": 3.0, "sleep_baseline": 7.0}
    feats = extract_features_from_history(history, baseline)
    assert feats["mood_deviation"] == -4.0
    assert feats["stress_deviation"] == 5.0
    assert feats["sleep_deviation"] == -3.0
