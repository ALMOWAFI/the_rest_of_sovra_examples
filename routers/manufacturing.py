import random
from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

router = APIRouter(prefix="/manufacturing", tags=["Smart Manufacturing"])


class Question(BaseModel):
    question: str
    defect_id: int = 0  # index from /analyze response, 0 = use session default


DEFECTS = [
    {
        "id": 0,
        "defect": "Short Circuit",
        "severity": "critical",
        "confidence": 97,
        "location": "Dense conductor routing area — center zone",
        "action": "Reject board immediately. Do not ship. Quarantine this batch and escalate to engineering.",
        "cause": "Copper etching inconsistency — chemical bath temperature deviated ±3°C above spec during this production window.",
        "prevention": "Recalibrate etching bath temperature sensor. Increase QC sampling rate to every 50 units until stable.",
        "safe_to_ship": False,
    },
    {
        "id": 1,
        "defect": "Solder Bridge",
        "severity": "high",
        "confidence": 94,
        "location": "IC pin array — lower left quadrant",
        "action": "Rework required. Apply precision solder wick to affected pins. Re-inspect after rework.",
        "cause": "Excess solder paste deposition during screen printing. Stencil aperture may be worn.",
        "prevention": "Replace stencil aperture for this component type. Verify paste volume with SPI before next run.",
        "safe_to_ship": False,
    },
    {
        "id": 2,
        "defect": "Base Material Scratch",
        "severity": "medium",
        "confidence": 88,
        "location": "Substrate surface — edge region (non-functional zone)",
        "action": "Manual inspection recommended. If scratch depth < 0.1mm and no conductor damage, board may pass.",
        "cause": "Mechanical handling damage — likely during conveyor transfer between stations.",
        "prevention": "Install soft edge guards on conveyor transfer points. Review board handling SOPs with operators.",
        "safe_to_ship": None,  # needs manual review
    },
    {
        "id": 3,
        "defect": "Missing Component",
        "severity": "high",
        "confidence": 99,
        "location": "Component placement zone — R47 position",
        "action": "Stop the line. Check component feeder for the affected reel. Rework all affected boards.",
        "cause": "Component feeder jam or empty reel not flagged by placement machine sensor.",
        "prevention": "Calibrate feeder presence sensors. Enable pre-run feeder verification check.",
        "safe_to_ship": False,
    },
    {
        "id": 4,
        "defect": "No Defect Detected",
        "severity": "none",
        "confidence": 99,
        "location": "Full board scan — all zones clear",
        "action": "Board passes inspection. Proceed to next production stage.",
        "cause": "N/A",
        "prevention": "Continue standard QC sampling protocol.",
        "safe_to_ship": True,
    },
]

KB = [
    {
        "keywords": ["cause", "why", "reason", "happen", "from", "origin", "what caused"],
        "handler": lambda d: {
            "title": "Root Cause Analysis",
            "answer": d["cause"],
            "details": [
                f"Defect: {d['defect']}",
                f"Confidence: {d['confidence']}%",
                f"Location: {d['location']}",
                "This is a process-level issue — investigate before continuing the production run.",
            ],
        },
    },
    {
        "keywords": ["ship", "batch", "safe", "pass", "release", "approve", "ok", "send"],
        "handler": lambda d: {
            "title": "Batch Release Decision",
            "answer": (
                "✓ Board passes inspection. Batch is safe to proceed."
                if d["safe_to_ship"] is True
                else "⚠ Batch should NOT be released until defective units are removed and root cause is addressed."
                if d["safe_to_ship"] is False
                else "⚠ Manual review required before batch release decision can be made."
            ),
            "details": [
                f"Detected defect: {d['defect']}",
                f"Severity: {d['severity'].upper()}",
                f"Confidence: {d['confidence']}%",
            ],
        },
    },
    {
        "keywords": ["repair", "rework", "fix", "action", "recommend", "do", "should", "next"],
        "handler": lambda d: {
            "title": "Recommended Action",
            "answer": d["action"],
            "details": [
                f"Defect: {d['defect']}",
                f"Location: {d['location']}",
                f"Confidence: {d['confidence']}%",
            ],
        },
    },
    {
        "keywords": ["prevent", "prevention", "avoid", "future", "stop", "recur", "again", "reduce"],
        "handler": lambda d: {
            "title": "Prevention Recommendation",
            "answer": d["prevention"],
            "details": [
                "Implementing this change is estimated to reduce similar defects by 60–80%.",
                f"Based on root cause: {d['cause']}",
            ],
        },
    },
    {
        "keywords": ["location", "where", "zone", "area", "position", "which part"],
        "handler": lambda d: {
            "title": "Defect Location",
            "answer": f"Defect detected at: {d['location']}",
            "details": [
                f"Defect type: {d['defect']}",
                "Functional impact: " + (
                    "high — circuit paths may be compromised"
                    if d["severity"] in ("critical", "high")
                    else "low — non-functional zone affected"
                ),
            ],
        },
    },
    {
        "keywords": ["confidence", "accurate", "sure", "certain", "score", "percent", "reliable"],
        "handler": lambda d: {
            "title": "Detection Confidence",
            "answer": f"Detected with {d['confidence']}% confidence.",
            "details": [
                "≥95%: High confidence — reliable for automated decision-making" if d["confidence"] >= 95
                else "≥80%: Good confidence — spot-check confirmation recommended" if d["confidence"] >= 80
                else "Moderate confidence — manual inspection recommended before action",
                f"Defect: {d['defect']}",
            ],
        },
    },
]

FALLBACK_HANDLER = lambda d: {
    "title": "Production Intelligence",
    "answer": f"Detected: {d['defect']} ({d['confidence']}% confidence) at {d['location']}.",
    "details": [f"Recommended action: {d['action']}"],
}


def match_question(question: str, defect: dict) -> dict:
    q = question.lower()
    best, top = None, 0
    for item in KB:
        score = sum(1 for k in item["keywords"] if k in q)
        if score > top:
            top, best = score, item["handler"]
    return (best or FALLBACK_HANDLER)(defect)


@router.post("/analyze")
async def analyze(image: UploadFile = File(...)):
    """Upload a production line image. Returns defect analysis."""
    # Mock: rotate through defects for demo variety
    defect = random.choice(DEFECTS)
    return {
        "defect_id": defect["id"],
        "defect": defect["defect"],
        "severity": defect["severity"],
        "confidence": defect["confidence"],
        "location": defect["location"],
        "action": defect["action"],
        "safe_to_ship": defect["safe_to_ship"],
    }


@router.post("/ask")
def ask(payload: Question):
    """Ask a follow-up question about the analyzed defect. Pass defect_id from /analyze."""
    defect = next((d for d in DEFECTS if d["id"] == payload.defect_id), DEFECTS[0])
    return match_question(payload.question, defect)
