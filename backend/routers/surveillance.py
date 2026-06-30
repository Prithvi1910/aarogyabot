"""
Community outbreak surveillance.

Aggregates the anonymized symptom/triage signals produced by ordinary chat usage
into regional clusters, so a possible disease outbreak can be flagged early. This
turns AarogyaBot from a per-patient assistant into a public-health early-warning tool.

Reports are kept in memory (no personal data — only a PIN code area, symptom
keywords, a triage level, and a timestamp).
"""
import time
import random
from collections import Counter, defaultdict
from datetime import datetime
from fastapi import APIRouter

router = APIRouter(prefix="/surveillance", tags=["Surveillance"])

# In-memory store of anonymized reports
_REPORTS = []  # {ts: float, pincode: str, symptoms: [str], level: str}

# How many reports of the same dominant symptom in one area triggers an alert
CLUSTER_THRESHOLD = 4
# Rolling window for "active" surveillance
WINDOW_DAYS = 7

# Symptom signatures used to name a likely disease behind a cluster
DISEASE_SIGNATURES = {
    "Dengue": {"fever", "rash", "joint pain"},
    "Malaria": {"fever", "chills", "headache"},
    "Cholera / Acute Diarrhoea": {"diarrhea", "vomiting"},
    "Typhoid": {"fever", "stomach pain", "diarrhea"},
    "Respiratory infection": {"cough", "fever"},
    "Chikungunya": {"fever", "joint pain", "rash"},
}


def log_report(pincode, symptoms, level):
    """Record an anonymized symptom report for surveillance."""
    if not symptoms:
        return
    _REPORTS.append({
        "ts": time.time(),
        "pincode": (pincode or "unknown").strip(),
        "symptoms": [s.lower().strip() for s in symptoms if s],
        "level": level,
    })


def _recent(days=WINDOW_DAYS):
    cutoff = time.time() - days * 86400
    return [r for r in _REPORTS if r["ts"] >= cutoff]


def _infer_disease(symptom_set):
    """Best-matching disease name for a set of symptoms in a cluster, or None."""
    best, best_overlap = None, 0
    for disease, sig in DISEASE_SIGNATURES.items():
        overlap = len(symptom_set & sig)
        # Require at least 2 overlapping symptoms to name a disease
        if overlap >= 2 and overlap > best_overlap:
            best, best_overlap = disease, overlap
    return best


def get_alerts():
    """Aggregate recent reports into regional clusters and summary stats."""
    recent = _recent()

    by_pin_symptoms = defaultdict(Counter)
    by_pin_total = Counter()
    symptom_counts = Counter()
    region_counts = Counter()

    for r in recent:
        symptom_counts.update(set(r["symptoms"]))
        if r["pincode"] and r["pincode"] != "unknown":
            by_pin_total[r["pincode"]] += 1
            region_counts[r["pincode"]] += 1
            for s in set(r["symptoms"]):
                by_pin_symptoms[r["pincode"]][s] += 1

    alerts = []
    for pin, symcount in by_pin_symptoms.items():
        top_sym, cnt = symcount.most_common(1)[0]
        if cnt >= CLUSTER_THRESHOLD:
            symptom_set = set(symcount.keys())
            disease = _infer_disease(symptom_set)
            top_symptoms = [s for s, _ in symcount.most_common(3)]
            alerts.append({
                "pincode": pin,
                "count": cnt,
                "total_reports": by_pin_total[pin],
                "symptoms": top_symptoms,
                "likely_condition": disease,
                "severity": "high" if cnt >= 8 else "moderate",
            })

    alerts.sort(key=lambda a: -a["count"])

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "window_days": WINDOW_DAYS,
        "total_reports": len(recent),
        "active_alerts": alerts[:6],
        "top_symptoms": [{"symptom": s, "count": c} for s, c in symptom_counts.most_common(6)],
        "regions": [{"pincode": p, "count": c} for p, c in region_counts.most_common(6)],
    }


@router.get("/alerts")
def alerts():
    return get_alerts()


def seed_demo_data():
    """Seed realistic demo clusters so the dashboard is meaningful during a demo."""
    if _REPORTS:
        return
    random.seed(7)
    now = time.time()

    # (pincode, symptoms, triage level, number of reports)
    demo = [
        ("400001", ["fever", "rash", "joint pain"], "VISIT_PHC", 11),   # dengue cluster (Mumbai)
        ("110001", ["diarrhea", "vomiting"], "VISIT_PHC", 8),           # diarrhoea cluster (Delhi)
        ("560001", ["cough", "fever"], "VISIT_PHC", 6),                 # respiratory (Bengaluru)
        ("700001", ["fever", "chills", "headache"], "VISIT_PHC", 5),    # malaria (Kolkata)
        ("400001", ["fever", "headache"], "SELF_CARE", 3),              # background noise
        ("110001", ["cough"], "SELF_CARE", 2),
    ]
    for pin, syms, lvl, count in demo:
        for _ in range(count):
            _REPORTS.append({
                "ts": now - random.randint(0, WINDOW_DAYS - 1) * 86400 - random.randint(0, 80000),
                "pincode": pin,
                "symptoms": syms,
                "level": lvl,
            })
