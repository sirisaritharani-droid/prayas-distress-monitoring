# PRAYAS (SIH26094 | Team SH-13)
### Dynamic Mental Health Monitoring and Distress Prediction System for Victims of Atrocities

> **Tagline:** Detect change. Understand risk. Enable human support.

---

## Key Innovations
1. **Personal Baseline vs Fixed Thresholds:** Calibrates to an individual's normal state rather than generic population averages.
2. **Dynamic Temporal Feature Engineering:** Tracks multi-day rate of change, rolling averages, and consecutive deterioration counts.
3. **Calibrated ML Risk Engine:** Probability-calibrated Random Forest (Sigmoid) tuned for high sensitivity/recall.
4. **Transparent Explainability:** Quantifies exact deviations driving elevated risk estimates.
5. **Human-in-the-Loop Triage:** Equips counsellors with prioritized caseload management.

---

## Quickstart Deployment

```bash
# 1. Unzip the archive
unzip prayas_sih26094_full_project.zip
cd prayas

# 2. Setup Virtual Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Generate Data & Train Model
python ml/generate_synthetic_data.py
python ml/train.py

# 4. Start Backend API (Terminal 1)
uvicorn backend.main:app --reload --port 8000

# 5. Start Frontend Dashboard (Terminal 2)
streamlit run frontend/streamlit_app.py

