import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_synthetic_cohort(n_users: int = 150, days_per_user: int = 21, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    records = []
    base_date = datetime.now() - timedelta(days=days_per_user + 2)

    for user_idx in range(1, n_users + 1):
        user_id = f"P-{100 + user_idx}"
        trajectory_type = np.random.choice(
            ["stable", "gradual_deterioration", "sudden_spike", "recovery"],
            p=[0.40, 0.25, 0.20, 0.15]
        )

        b_mood = np.random.uniform(6.5, 8.5)
        b_stress = np.random.uniform(2.0, 4.0)
        b_anxiety = np.random.uniform(2.0, 4.0)
        b_sleep = np.random.uniform(6.8, 8.5)
        b_social = np.random.uniform(6.0, 8.5)
        b_safety = np.random.uniform(6.5, 9.0)
        b_energy = np.random.uniform(6.0, 8.5)

        for d in range(days_per_user):
            timestamp = base_date + timedelta(days=d, hours=int(np.random.randint(8, 20)))
            
            if trajectory_type == "stable":
                curr_mood = np.clip(b_mood + np.random.normal(0, 0.4), 1, 10)
                curr_stress = np.clip(b_stress + np.random.normal(0, 0.4), 1, 10)
                curr_anxiety = np.clip(b_anxiety + np.random.normal(0, 0.4), 1, 10)
                curr_sleep = np.clip(b_sleep + np.random.normal(0, 0.4), 2, 12)
                curr_social = np.clip(b_social + np.random.normal(0, 0.5), 1, 10)
                curr_safety = np.clip(b_safety + np.random.normal(0, 0.4), 1, 10)
                curr_energy = np.clip(b_energy + np.random.normal(0, 0.5), 1, 10)
                target_distress_risk = 0

            elif trajectory_type == "gradual_deterioration":
                decay_factor = d / float(days_per_user)
                curr_mood = np.clip(b_mood - (4.0 * decay_factor) + np.random.normal(0, 0.3), 1, 10)
                curr_stress = np.clip(b_stress + (5.0 * decay_factor) + np.random.normal(0, 0.3), 1, 10)
                curr_anxiety = np.clip(b_anxiety + (4.5 * decay_factor) + np.random.normal(0, 0.3), 1, 10)
                curr_sleep = np.clip(b_sleep - (3.2 * decay_factor) + np.random.normal(0, 0.4), 2, 12)
                curr_social = np.clip(b_social - (3.5 * decay_factor) + np.random.normal(0, 0.4), 1, 10)
                curr_safety = np.clip(b_safety - (3.0 * decay_factor) + np.random.normal(0, 0.4), 1, 10)
                curr_energy = np.clip(b_energy - (3.8 * decay_factor) + np.random.normal(0, 0.4), 1, 10)
                target_distress_risk = 1 if decay_factor > 0.45 else 0

            elif trajectory_type == "sudden_spike":
                if d >= 14:
                    curr_mood = np.clip(b_mood - 4.5 + np.random.normal(0, 0.4), 1, 10)
                    curr_stress = np.clip(b_stress + 5.5 + np.random.normal(0, 0.4), 1, 10)
                    curr_anxiety = np.clip(b_anxiety + 5.0 + np.random.normal(0, 0.4), 1, 10)
                    curr_sleep = np.clip(b_sleep - 3.8 + np.random.normal(0, 0.5), 2, 12)
                    curr_social = np.clip(b_social - 4.0 + np.random.normal(0, 0.5), 1, 10)
                    curr_safety = np.clip(b_safety - 5.0 + np.random.normal(0, 0.5), 1, 10)
                    curr_energy = np.clip(b_energy - 4.5 + np.random.normal(0, 0.4), 1, 10)
                    target_distress_risk = 1
                else:
                    curr_mood = np.clip(b_mood + np.random.normal(0, 0.3), 1, 10)
                    curr_stress = np.clip(b_stress + np.random.normal(0, 0.3), 1, 10)
                    curr_anxiety = np.clip(b_anxiety + np.random.normal(0, 0.3), 1, 10)
                    curr_sleep = np.clip(b_sleep + np.random.normal(0, 0.3), 2, 12)
                    curr_social = np.clip(b_social + np.random.normal(0, 0.3), 1, 10)
                    curr_safety = np.clip(b_safety + np.random.normal(0, 0.3), 1, 10)
                    curr_energy = np.clip(b_energy + np.random.normal(0, 0.3), 1, 10)
                    target_distress_risk = 0

            else:
                progress = d / float(days_per_user)
                curr_mood = np.clip(3.0 + (4.5 * progress) + np.random.normal(0, 0.3), 1, 10)
                curr_stress = np.clip(8.0 - (4.5 * progress) + np.random.normal(0, 0.3), 1, 10)
                curr_anxiety = np.clip(7.5 - (4.0 * progress) + np.random.normal(0, 0.3), 1, 10)
                curr_sleep = np.clip(4.0 + (3.5 * progress) + np.random.normal(0, 0.4), 2, 12)
                curr_social = np.clip(3.5 + (3.8 * progress) + np.random.normal(0, 0.4), 1, 10)
                curr_safety = np.clip(4.0 + (3.5 * progress) + np.random.normal(0, 0.4), 1, 10)
                curr_energy = np.clip(3.5 + (4.0 * progress) + np.random.normal(0, 0.4), 1, 10)
                target_distress_risk = 1 if progress < 0.4 else 0

            records.append({
                "user_id": user_id,
                "timestamp": timestamp.isoformat(),
                "day_index": d,
                "mood": round(float(curr_mood), 1),
                "stress": round(float(curr_stress), 1),
                "anxiety": round(float(curr_anxiety), 1),
                "sleep_hours": round(float(curr_sleep), 1),
                "social_connection": round(float(curr_social), 1),
                "safety": round(float(curr_safety), 1),
                "energy": round(float(curr_energy), 1),
                "trajectory_type": trajectory_type,
                "high_distress_flag": target_distress_risk
            })

    df = pd.DataFrame(records)
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "longitudinal_distress_dataset.csv")
    df.to_csv(out_path, index=False)
    print(f"[PRAYAS ML] Generated {len(df)} synthetic records at: {out_path}")
    return df

if __name__ == "__main__":
    generate_synthetic_cohort()
