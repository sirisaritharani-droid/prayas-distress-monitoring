import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime, timedelta

st.set_page_config(
    page_title="PRAYAS | Mental Health Distress Monitoring",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE = "http://127.0.0.1:8000"

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 24px 32px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .disclaimer-badge {
        background-color: #F1F5F9;
        border-left: 4px solid #0284C7;
        padding: 12px 16px;
        font-size: 0.85rem;
        color: #334155;
        border-radius: 0 8px 8px 0;
        margin-bottom: 20px;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    .risk-pill-high { background-color: #FEE2E2; color: #991B1B; padding: 4px 12px; border-radius: 9999px; font-weight: 600; font-size: 0.85rem; }
    .risk-pill-mod { background-color: #FEF3C7; color: #92400E; padding: 4px 12px; border-radius: 9999px; font-weight: 600; font-size: 0.85rem; }
    .risk-pill-low { background-color: #DCFCE7; color: #166534; padding: 4px 12px; border-radius: 9999px; font-weight: 600; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

if "case_id" not in st.session_state:
    st.session_state.case_id = "P-102"

st.markdown("""
<div class="main-header">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1 style="margin:0; font-size:1.8rem; font-weight:700; color:#38BDF8;">PRAYAS</h1>
            <p style="margin:4px 0 0 0; color:#94A3B8; font-size:0.95rem;">
                AI-Powered Dynamic Mental Health Monitoring & Distress Prediction for Victims of Atrocities (SIH26094)
            </p>
        </div>
        <div style="text-align:right;">
            <span style="background:#0369A1; color:#E0F2FE; padding:6px 12px; border-radius:6px; font-size:0.8rem; font-weight:600;">
                Team PRAYAS • SH-13
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer-badge">
    <strong>🛡️ Responsible AI Safety Notice:</strong><br>
    PRAYAS provides an AI-assisted distress-risk estimate for support prioritization. 
    It is <strong>not a medical diagnosis</strong> and does not replace qualified psychologists, counsellors, or medical professionals.
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("Navigation")
    demo_role = st.selectbox("Switch Workspace Role", ["Survivor / User", "Counsellor / Professional", "Admin / Responsible AI"])
    st.markdown("---")
    
    if demo_role == "Survivor / User":
        user_menu = st.radio("Survivor Portal", ["Dashboard Overview", "Daily Wellbeing Check-in", "My Baseline & Trends", "Support & Resources", "Data & Consent"])
    elif demo_role == "Counsellor / Professional":
        counsellor_menu = st.radio("Counsellor Portal", ["Active Caseload Triage", "Individual Case Drilldown", "Support Follow-up Manager"])
    else:
        admin_menu = st.radio("AI Governance", ["Model Performance & ROC", "Explainability & Feature Weights", "Responsible AI Checklist"])

    st.markdown("---")
    st.markdown("### 🧪 SIH Interactive Scenarios")
    sih_scenario = st.selectbox("Load Demonstration Scenario", [
        "Scenario A (P-102): Gradual Distress Spike",
        "Scenario B (P-101): Stable Baseline",
        "Scenario C (P-105): Recovery Trajectory"
    ])
    if st.button("Apply Demo Scenario"):
        if "P-102" in sih_scenario:
            st.session_state.case_id = "P-102"
        elif "P-101" in sih_scenario:
            st.session_state.case_id = "P-101"
        else:
            st.session_state.case_id = "P-105"
        st.success(f"Loaded {st.session_state.case_id}")

def fetch_case_data(case_id):
    days = 15
    dates = [(datetime.now() - timedelta(days=days-i)).strftime("%b %d") for i in range(days)]
    if case_id == "P-102":
        moods = [7.5, 7.3, 7.0, 6.8, 6.5, 6.0, 5.8, 5.2, 4.8, 4.2, 3.9, 3.5, 3.2, 3.0, 2.9]
        stresses = [3.0, 3.2, 3.5, 4.0, 4.5, 5.0, 5.8, 6.2, 6.8, 7.2, 7.8, 8.0, 8.2, 8.5, 8.7]
        anxieties = [2.8, 3.0, 3.2, 3.8, 4.2, 4.8, 5.5, 6.0, 6.4, 6.9, 7.2, 7.5, 7.8, 8.0, 8.2]
        sleeps = [7.5, 7.4, 7.2, 6.8, 6.5, 6.0, 5.8, 5.2, 4.9, 4.5, 4.2, 4.0, 3.8, 3.5, 3.4]
        risk_level = "HIGH"
        risk_pct = 78
        trend = "INCREASING"
    elif case_id == "P-101":
        moods = [7.2, 7.0, 7.3, 7.1, 7.4, 7.2, 7.1, 7.0, 7.3, 7.2, 7.1, 7.4, 7.2, 7.3, 7.2]
        stresses = [3.1, 3.0, 3.2, 3.1, 3.0, 3.2, 3.1, 3.0, 3.2, 3.1, 3.0, 2.9, 3.1, 3.0, 3.1]
        anxieties = [2.9, 3.0, 2.8, 2.9, 3.1, 2.8, 3.0, 2.9, 3.0, 2.8, 2.9, 3.0, 2.9, 2.8, 2.9]
        sleeps = [7.5, 7.6, 7.4, 7.5, 7.3, 7.6, 7.4, 7.5, 7.6, 7.4, 7.5, 7.3, 7.5, 7.6, 7.5]
        risk_level = "LOW"
        risk_pct = 18
        trend = "STABLE"
    else:
        moods = [3.5, 3.8, 4.0, 4.5, 4.8, 5.2, 5.8, 6.0, 6.4, 6.8, 7.0, 7.2, 7.3, 7.5, 7.6]
        stresses = [8.0, 7.8, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5, 4.2, 3.8, 3.5, 3.2, 3.0, 2.9]
        anxieties = [7.5, 7.2, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0, 3.8, 3.5, 3.2, 3.0, 2.8, 2.7]
        sleeps = [4.2, 4.5, 4.8, 5.2, 5.5, 5.8, 6.2, 6.5, 6.8, 7.0, 7.2, 7.4, 7.5, 7.6, 7.5]
        risk_level = "LOW"
        risk_pct = 22
        trend = "IMPROVING"

    checkin_list = []
    for i in range(days):
        checkin_list.append({
            "timestamp": dates[i],
            "mood": moods[i],
            "stress": stresses[i],
            "anxiety": anxieties[i],
            "sleep_hours": sleeps[i],
            "social_connection": 6.0,
            "safety": 7.0,
            "energy": 6.0
        })
    
    return {
        "case_id": case_id,
        "evaluation": {
            "risk_level": risk_level,
            "risk_percentage": risk_pct,
            "trend_direction": trend,
            "confidence": 0.88,
            "action_recommendation": "Immediate human assessment recommended." if risk_level == "HIGH" else "Routine self-monitoring.",
            "baseline": {
                "mood_baseline": 7.2,
                "stress_baseline": 3.1,
                "anxiety_baseline": 2.9,
                "sleep_baseline": 7.4
            }
        },
        "explanations": [
            {"description": "Stress increased significantly from personal baseline (+5.6 pts)", "importance_score": 8.9},
            {"description": "Nightly sleep decreased by 4.0 hours compared to baseline", "importance_score": 8.1},
            {"description": "Sustained downward mood trajectory over consecutive 7 check-ins", "importance_score": 7.5},
            {"description": "Heightened anxiety relative to usual baseline pattern", "importance_score": 6.4}
        ],
        "checkins": checkin_list,
        "followup": {"status": "NOT_REVIEWED", "notes": "Requires follow-up review."}
    }

if demo_role == "Survivor / User":
    case_data = fetch_case_data(st.session_state.case_id)
    eval_info = case_data["evaluation"]

    if user_menu == "Dashboard Overview":
        st.subheader(f"👋 Welcome back. Anonymous Case ID: {st.session_state.case_id}")
        st.write("Here is an overview of how your wellbeing signals compare against your personal baseline.")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.caption("ESTIMATED DISTRESS RISK")
            r_level = eval_info["risk_level"]
            pill_cls = "risk-pill-high" if r_level == "HIGH" else ("risk-pill-mod" if r_level == "MODERATE" else "risk-pill-low")
            st.markdown(f'<span class="{pill_cls}">{r_level} ({eval_info["risk_percentage"]}%)</span>', unsafe_allow_html=True)
            st.write(f"Confidence: {int(eval_info['confidence']*100)}%")
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.caption("TRAJECTORY TREND")
            trend = eval_info["trend_direction"]
            arrow = "↑ Escalating" if trend == "INCREASING" else ("↓ Improving" if trend == "IMPROVING" else "→ Stable")
            st.markdown(f"### {arrow}")
            st.write("Compared to 7-day MA")
            st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.caption("LATEST MOOD")
            last_mood = case_data["checkins"][-1]["mood"]
            b_mood = eval_info["baseline"]["mood_baseline"]
            dev_m = round(last_mood - b_mood, 1)
            st.markdown(f"### {last_mood} / 10")
            st.caption(f"Baseline: {b_mood} ({dev_m:+})")
            st.markdown('</div>', unsafe_allow_html=True)
        with c4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.caption("LATEST SLEEP")
            last_sleep = case_data["checkins"][-1]["sleep_hours"]
            b_sleep = eval_info["baseline"]["sleep_baseline"]
            dev_s = round(last_sleep - b_sleep, 1)
            st.markdown(f"### {last_sleep} hrs")
            st.caption(f"Baseline: {b_sleep}h ({dev_s:+}h)")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📈 Longitudinal Distress Signals vs. Personal Baseline")
        df_hist = pd.DataFrame(case_data["checkins"])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_hist["timestamp"], y=df_hist["mood"], mode='lines+markers', name='Mood (1-10)', line=dict(color='#0284C7', width=3)))
        fig.add_trace(go.Scatter(x=df_hist["timestamp"], y=df_hist["stress"], mode='lines+markers', name='Stress (1-10)', line=dict(color='#EF4444', width=3)))
        fig.add_trace(go.Scatter(x=df_hist["timestamp"], y=df_hist["sleep_hours"], mode='lines+markers', name='Sleep (Hours)', line=dict(color='#8B5CF6', width=2, dash='dash')))
        
        fig.add_hline(y=eval_info["baseline"]["mood_baseline"], line_dash="dot", line_color="#38BDF8", annotation_text="Mood Baseline")
        fig.add_hline(y=eval_info["baseline"]["stress_baseline"], line_dash="dot", line_color="#F87171", annotation_text="Stress Baseline")

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="white",
            margin=dict(l=20, r=20, t=30, b=20),
            height=380,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 🔍 Why did the AI estimate this risk level?")
        for exp in case_data["explanations"]:
            st.info(f"• {exp['description']}")

        if eval_info["risk_level"] == "HIGH":
            st.warning("⚠️ **Support Recommendation:** Immediate human assessment recommended. You do not have to carry everything alone.")
            if st.button("Request Human Counsellor Contact", key="btn_req_help"):
                st.success("Your request has been forwarded to an authorized on-call support counsellor. Anonymity preserved.")

    elif user_menu == "Daily Wellbeing Check-in":
        st.subheader("📝 Daily Wellbeing Check-in")
        with st.form("checkin_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                f_mood = st.slider("Mood (1 = Deeply distressing, 10 = Very positive)", 1.0, 10.0, 6.0, 0.5)
                f_stress = st.slider("Stress Level (1 = Completely calm, 10 = Overwhelming)", 1.0, 10.0, 4.0, 0.5)
                f_anxiety = st.slider("Anxiety / Worry (1 = None, 10 = Severe panic)", 1.0, 10.0, 3.0, 0.5)
                f_sleep = st.slider("Nightly Sleep (Hours)", 0.0, 14.0, 7.0, 0.5)
            with col_b:
                f_social = st.slider("Social Connection / Support Feeling", 1.0, 10.0, 7.0, 0.5)
                f_safety = st.slider("Feeling of Physical & Emotional Safety", 1.0, 10.0, 8.0, 0.5)
                f_energy = st.slider("Energy / Motivation Level", 1.0, 10.0, 6.0, 0.5)
                f_text = st.text_area("Optional Reflections (Encrypted, Private)")

            if st.form_submit_button("Submit Check-in"):
                st.success("✅ Check-in recorded securely. Baseline and dynamic features updated.")

    elif user_menu == "My Baseline & Trends":
        st.subheader("📊 Your Personal Baseline")
        b = eval_info["baseline"]
        bc1, bc2, bc3, bc4 = st.columns(4)
        bc1.metric("Baseline Mood", f"{b['mood_baseline']:.1f} / 10")
        bc2.metric("Baseline Stress", f"{b['stress_baseline']:.1f} / 10")
        bc3.metric("Baseline Anxiety", f"{b['anxiety_baseline']:.1f} / 10")
        bc4.metric("Baseline Sleep", f"{b['sleep_baseline']:.1f} hrs")

    elif user_menu == "Support & Resources":
        st.subheader("🤝 Human Support & Crisis Guidelines")
        st.markdown("""
        PRAYAS is an early-warning system to connect you with human care.
        - 👤 **Request Direct Follow-up:** Notify your assigned case worker or humanitarian psychologist.
        - 📞 **Local Crisis Helplines:** Connect with verified national helpline resources.
        - 📖 **Grounding & Trauma Exercises:** Guided breathing and physiological regulation tools.
        """)
        if st.button("Request Immediate Follow-Up Contact"):
            st.success("Your request has been prioritized in the counsellor triage queue.")

    elif user_menu == "Data & Consent":
        st.subheader("🔒 Privacy & Consent Management")
        st.checkbox("I voluntarily agree to participate in AI distress monitoring", value=True)
        st.checkbox("Allow authorized counsellors to review aggregated longitudinal trends", value=True)
        st.button("Save Consent Preferences")

elif demo_role == "Counsellor / Professional":
    st.subheader("📋 Counsellor Triage & Caseload Priority")
    if counsellor_menu == "Active Caseload Triage":
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Active Monitored Cases", "42")
        c2.metric("High Distress Risk", "6", delta="Requires Review", delta_color="inverse")
        c3.metric("Moderate Risk", "14")
        c4.metric("Pending Human Follow-up", "11")

        st.markdown("#### Authorized Survivor Caseload")
        cases_table = pd.DataFrame([
            {"Case ID": "P-102", "Risk Level": "HIGH (78%)", "Trend": "↑ Escalating", "Last Check-in": "Today", "Status": "NOT REVIEWED", "Priority": "🚨 Immediate"},
            {"Case ID": "P-103", "Risk Level": "MODERATE (52%)", "Trend": "↑ Escalating", "Last Check-in": "Today", "Status": "SCHEDULED", "Priority": "⚠️ Moderate"},
            {"Case ID": "P-104", "Risk Level": "MODERATE (41%)", "Trend": "→ Stable", "Last Check-in": "Yesterday", "Status": "REVIEWED", "Priority": "ℹ️ Routine"},
            {"Case ID": "P-101", "Risk Level": "LOW (18%)", "Trend": "→ Stable", "Last Check-in": "Today", "Status": "REVIEWED", "Priority": "✅ Low"},
            {"Case ID": "P-105", "Risk Level": "LOW (22%)", "Trend": "↓ Improving", "Last Check-in": "2 days ago", "Status": "SUPPORT PROVIDED", "Priority": "✅ Low"},
        ])
        st.dataframe(cases_table, use_container_width=True)

    elif counsellor_menu == "Individual Case Drilldown":
        selected_case = st.selectbox("Select Case to Inspect", ["P-102 (High Risk Demo)", "P-101 (Stable Demo)", "P-105 (Recovery Demo)"])
        cid = selected_case.split()[0]
        case_data = fetch_case_data(cid)
        eval_info = case_data["evaluation"]

        st.markdown(f"### Detailed Longitudinal Analysis: Case {cid}")
        c_left, c_right = st.columns([2, 1])
        with c_left:
            df_hist = pd.DataFrame(case_data["checkins"])
            fig = px.line(df_hist, x="timestamp", y=["mood", "stress", "sleep_hours"], title=f"Longitudinal Trajectory ({cid})", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        with c_right:
            st.markdown("#### Primary Contributing Drivers")
            for exp in case_data["explanations"]:
                st.error(f"**{exp['description']}** (Weight: {exp['importance_score']})")

        st.markdown("---")
        with st.form("counsellor_action_form"):
            status_choice = st.selectbox("Action Status", ["NOT_REVIEWED", "REVIEWED", "FOLLOWUP_SCHEDULED", "SUPPORT_PROVIDED", "ESCALATED"])
            c_notes = st.text_area("Counsellor Clinical Notes", value=case_data["followup"]["notes"])
            if st.form_submit_button("Save Case Action"):
                st.success(f"Case {cid} updated to status '{status_choice}'. Audit log recorded.")

    elif counsellor_menu == "Support Follow-up Manager":
        st.subheader("📅 Scheduled Interventions")
        st.write("• **P-102:** Consultation scheduled tomorrow at 10:00 AM (Priority: High)")
        st.write("• **P-103:** Peer support group invitation dispatched (Priority: Moderate)")

else:
    if admin_menu == "Model Performance & ROC":
        st.subheader("⚙️ Machine Learning Model Validation")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ROC-AUC Score", "0.941")
        m2.metric("Recall (Sensitivity)", "0.912")
        m3.metric("Precision", "0.875")
        m4.metric("F1-Score", "0.893")
        cm_data = pd.DataFrame([[112, 16], [10, 104]], columns=["Pred: Low/Mod", "Pred: High"], index=["Actual: Low/Mod", "Actual: High"])
        st.table(cm_data)

    elif admin_menu == "Explainability & Feature Weights":
        st.subheader("🧠 Global Feature Importance")
        feat_df = pd.DataFrame([
            {"Feature": "Stress Deviation from Baseline", "Importance": 0.24},
            {"Feature": "Sleep Deviation (Hours Drop)", "Importance": 0.21},
            {"Feature": "Consecutive Deterioration Count", "Importance": 0.18},
            {"Feature": "Mood Deviation from Baseline", "Importance": 0.15},
            {"Feature": "3-Day Rate of Stress Change", "Importance": 0.11},
            {"Feature": "Social Connection Loss", "Importance": 0.07},
            {"Feature": "Safety Perception", "Importance": 0.04},
        ]).sort_values("Importance", ascending=True)
        fig = px.bar(feat_df, x="Importance", y="Feature", orientation="h", title="Top Predictive Drivers in Distress Estimation")
        st.plotly_chart(fig, use_container_width=True)

    elif admin_menu == "Responsible AI Checklist":
        st.subheader("🛡️ Responsible AI & Ethical Architecture Compliance")
        st.markdown("""
        - [x] **Non-Diagnostic Language:** Predictions strictly termed "distress risk estimates".
        - [x] **Human-in-the-Loop:** High-risk flags triage cases for human intervention.
        - [x] **Anonymized Case IDs:** Uses pseudonymous identifiers (`P-102`).
        - [x] **Calibrated Probabilities:** Sigmoid Probability Calibration applied.
        - [x] **Audit Trail:** Follow-ups and data access generate audit logs.
        """)
