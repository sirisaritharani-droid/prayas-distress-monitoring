import sys
import os
import random
import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ml"))

from database import engine, Base, get_db
import models, schemas, auth
from features import calculate_baseline
from predict import evaluate_distress_risk
from explain import explain_prediction

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PRAYAS Mental Health Monitoring API",
    description="Privacy-First AI-Assisted Distress-Risk Monitoring for Atrocity Victims",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def populate_demo_database():
    db = next(get_db())
    if db.query(models.User).count() == 0:
        print("[PRAYAS] Initializing demonstration database with preloaded cohorts...")
        counsellor = models.User(
            email="counsellor@prayas.org",
            anonymous_case_id="STAFF-01",
            password_hash=auth.get_password_hash("support123"),
            role="counsellor"
        )
        db.add(counsellor)
        db.commit()

        demo_scenarios = [
            ("user_stable@prayas.org", "P-101", "stable"),
            ("user_deteriorating@prayas.org", "P-102", "deteriorating"),
            ("user_moderate@prayas.org", "P-103", "moderate_spike"),
            ("user_recovering@prayas.org", "P-105", "recovering")
        ]

        base_time = datetime.datetime.utcnow() - datetime.timedelta(days=16)

        for email, case_id, trajectory in demo_scenarios:
            usr = models.User(
                email=email,
                anonymous_case_id=case_id,
                password_hash=auth.get_password_hash("pass123"),
                role="survivor"
            )
            db.add(usr)
            db.commit()
            db.refresh(usr)

            consent = models.Consent(user_id=usr.id, accepted=True, share_optional_signals=True)
            db.add(consent)

            for d in range(15):
                cur_dt = base_time + datetime.timedelta(days=d)
                if trajectory == "stable":
                    m, s, a, sl = 7.2, 3.1, 2.9, 7.5
                elif trajectory == "deteriorating":
                    prog = d / 14.0
                    m = 7.5 - (4.5 * prog)
                    s = 3.0 + (5.2 * prog)
                    a = 2.8 + (4.4 * prog)
                    sl = 7.5 - (3.5 * prog)
                elif trajectory == "moderate_spike":
                    prog = d / 14.0
                    m = 6.5 - (2.0 * prog)
                    s = 4.0 + (2.5 * prog)
                    a = 3.5 + (2.5 * prog)
                    sl = 7.0 - (1.5 * prog)
                else:
                    prog = d / 14.0
                    m = 3.5 + (3.5 * prog)
                    s = 7.8 - (4.2 * prog)
                    a = 7.0 - (3.8 * prog)
                    sl = 4.5 + (2.8 * prog)

                checkin = models.CheckIn(
                    user_id=usr.id,
                    timestamp=cur_dt,
                    mood=round(max(1.0, min(10.0, m + random.uniform(-0.2, 0.2))), 1),
                    stress=round(max(1.0, min(10.0, s + random.uniform(-0.2, 0.2))), 1),
                    anxiety=round(max(1.0, min(10.0, a + random.uniform(-0.2, 0.2))), 1),
                    sleep_hours=round(max(2.0, min(12.0, sl + random.uniform(-0.2, 0.2))), 1),
                    social_connection=6.5,
                    safety=7.0,
                    energy=6.0
                )
                db.add(checkin)

            fu = models.FollowUp(
                user_id=usr.id,
                status="NOT_REVIEWED" if trajectory == "deteriorating" else "REVIEWED",
                notes="Primary test case" if case_id == "P-102" else "Routine monitoring"
            )
            db.add(fu)
            db.commit()

@app.post("/auth/register", response_model=schemas.Token)
def register(req: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")
    
    random_id = f"P-{random.randint(200, 999)}"
    new_user = models.User(
        email=req.email,
        anonymous_case_id=random_id,
        password_hash=auth.get_password_hash(req.password),
        role=req.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = auth.create_access_token({"sub": new_user.email, "role": new_user.role, "case_id": new_user.anonymous_case_id})
    return {"access_token": token, "token_type": "bearer", "role": new_user.role, "anonymous_case_id": new_user.anonymous_case_id}

@app.post("/auth/login", response_model=schemas.Token)
def login(req: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user or not auth.verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    token = auth.create_access_token({"sub": user.email, "role": user.role, "case_id": user.anonymous_case_id})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "anonymous_case_id": user.anonymous_case_id}

@app.post("/consent")
def submit_consent(req: schemas.ConsentRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    consent = models.Consent(user_id=current_user.id, accepted=req.accepted, share_optional_signals=req.share_optional_signals)
    db.add(consent)
    db.commit()
    return {"status": "success", "accepted": req.accepted}

@app.post("/checkins", response_model=schemas.CheckInResponse)
def create_checkin(req: schemas.CheckInCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    ts = req.custom_timestamp if req.custom_timestamp else datetime.datetime.utcnow()
    checkin = models.CheckIn(
        user_id=current_user.id,
        timestamp=ts,
        mood=req.mood,
        stress=req.stress,
        anxiety=req.anxiety,
        sleep_hours=req.sleep_hours,
        social_connection=req.social_connection,
        safety=req.safety,
        energy=req.energy,
        optional_text=req.optional_text
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin

@app.get("/counsellor/cases", response_model=List[schemas.CounsellorCaseSummary])
def get_counsellor_cases(counsellor: models.User = Depends(auth.require_counsellor), db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.role == "survivor").all()
    summaries = []

    for u in users:
        checkins = db.query(models.CheckIn).filter(models.CheckIn.user_id == u.id).order_by(models.CheckIn.timestamp.asc()).all()
        history = [{
            "timestamp": c.timestamp.isoformat(),
            "mood": c.mood,
            "stress": c.stress,
            "anxiety": c.anxiety,
            "sleep_hours": c.sleep_hours,
            "social_connection": c.social_connection,
            "safety": c.safety,
            "energy": c.energy
        } for c in checkins]

        eval_res = evaluate_distress_risk(history)
        fu = db.query(models.FollowUp).filter(models.FollowUp.user_id == u.id).first()
        status_val = fu.status if fu else "NOT_REVIEWED"

        last_date = checkins[-1].timestamp.strftime("%Y-%m-%d") if checkins else "None"
        summaries.append({
            "case_id": u.anonymous_case_id,
            "user_db_id": u.id,
            "risk_level": eval_res.get("risk_level", "LOW"),
            "risk_percentage": eval_res.get("risk_percentage", 0),
            "trend": eval_res.get("trend_direction", "STABLE"),
            "last_checkin_date": last_date,
            "followup_status": status_val,
            "needs_attention": eval_res.get("risk_level") == "HIGH" and status_val == "NOT_REVIEWED"
        })

    summaries.sort(key=lambda x: (0 if x["risk_level"] == "HIGH" else (1 if x["risk_level"] == "MODERATE" else 2), -x["risk_percentage"]))
    return summaries

@app.get("/counsellor/cases/{case_id}")
def get_case_detail(case_id: str, counsellor: models.User = Depends(auth.require_counsellor), db: Session = Depends(get_db)):
    target_user = db.query(models.User).filter(models.User.anonymous_case_id == case_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Case ID not found")

    checkins = db.query(models.CheckIn).filter(models.CheckIn.user_id == target_user.id).order_by(models.CheckIn.timestamp.asc()).all()
    history = [{
        "timestamp": c.timestamp.isoformat(),
        "mood": c.mood,
        "stress": c.stress,
        "anxiety": c.anxiety,
        "sleep_hours": c.sleep_hours,
        "social_connection": c.social_connection,
        "safety": c.safety,
        "energy": c.energy,
        "optional_text": c.optional_text
    } for c in checkins]

    eval_result = evaluate_distress_risk(history)
    explanations = explain_prediction(eval_result.get("features", {})) if eval_result.get("features") else []
    fu = db.query(models.FollowUp).filter(models.FollowUp.user_id == target_user.id).first()

    return {
        "case_id": target_user.anonymous_case_id,
        "evaluation": eval_result,
        "explanations": explanations,
        "checkins": history,
        "followup": {
            "status": fu.status if fu else "NOT_REVIEWED",
            "notes": fu.notes if fu else ""
        }
    }

@app.post("/counsellor/followup")
def update_followup(req: schemas.CounsellorUpdateFollowup, counsellor: models.User = Depends(auth.require_counsellor), db: Session = Depends(get_db)):
    target_user = db.query(models.User).filter(models.User.anonymous_case_id == req.case_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Case not found")

    fu = db.query(models.FollowUp).filter(models.FollowUp.user_id == target_user.id).first()
    if not fu:
        fu = models.FollowUp(user_id=target_user.id)
        db.add(fu)

    fu.status = req.status
    if req.notes:
        fu.notes = req.notes
    fu.updated_at = datetime.datetime.utcnow()
    db.commit()
    return {"status": "updated", "case_id": req.case_id, "new_status": req.status}

@app.get("/model/metrics")
def get_model_metrics():
    from predict import load_prayas_model
    art = load_prayas_model()
    return art.get("metrics", {})
