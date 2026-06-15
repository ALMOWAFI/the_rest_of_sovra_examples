from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/manufacturing", tags=["Smart Manufacturing"])


class Question(BaseModel):
    question: str
    site: str = "Berlin Electronics Plant"
    line_id: str | None = None


PLANT_SNAPSHOT = {
    "site": "Berlin Electronics Plant",
    "timestamp": "2026-06-14T08:30:00Z",
    "plant_oee": 78.4,
    "active_alerts": 3,
    "parts_per_hour": 231,
    "lines": {
        "LINE-1": {"oee": 83.1, "availability": 94.0, "performance": 89.4, "quality": 98.8, "status": "stable"},
        "LINE-2": {"oee": 74.2, "availability": 88.5, "performance": 86.7, "quality": 96.8, "status": "micro-stoppages"},
        "LINE-3": {"oee": 78.4, "availability": 91.2, "performance": 88.6, "quality": 96.9, "status": "performance loss"},
        "LINE-4": {"oee": 81.0, "availability": 92.6, "performance": 90.3, "quality": 96.9, "status": "stable"},
        "LINE-5": {"oee": 69.8, "availability": 84.7, "performance": 84.2, "quality": 98.0, "status": "maintenance watch"},
    },
}

KB = [
    {
        "keywords": ["oee", "efficiency", "line 3", "line three"],
        "response": {
            "title": "OEE for Line 3",
            "answer": "Line 3 OEE is 78.4%. Availability is 91.2%, performance is 88.6%, and quality is 96.9%.",
            "source": "MES Snapshot - Line 3, last 24h",
            "metrics": {
                "oee": "78.4%",
                "availability": "91.2%",
                "performance": "88.6%",
                "quality": "96.9%",
            },
            "recommendations": [
                "Investigate short micro-stoppages because performance is the largest loss factor",
                "Compare cycle-time drift between current and previous shift",
                "Review feeder changeover time for the last 3 production orders",
            ],
        },
    },
    {
        "keywords": ["maintenance", "alert", "alerts", "predictive", "vibration", "cnc", "today"],
        "response": {
            "title": "Maintenance Alerts",
            "answer": "There are 3 active maintenance alerts. The highest priority is CNC Unit 7 vibration above the 85th percentile for 4 hours.",
            "source": "Maintenance System - Active Alerts",
            "metrics": {
                "active_alerts": 3,
                "highest_priority_asset": "CNC Unit 7",
                "estimated_remaining_useful_life": "12-18 hours",
            },
            "recommendations": [
                "Schedule CNC Unit 7 inspection during the next planned downtime window",
                "Check spindle bearing temperature and lubrication history",
                "Keep Line 5 on maintenance watch until vibration trend returns to normal",
            ],
        },
    },
    {
        "keywords": ["production", "output", "scrap", "current shift", "shift summary", "parts"],
        "response": {
            "title": "Current Shift Production Summary",
            "answer": "The current shift produced 1,842 parts against a target of 2,100. Scrap rate is 1.8%, above the 1.2% target.",
            "source": "MES Shift Report - Current Shift",
            "metrics": {
                "produced": 1842,
                "target": 2100,
                "scrap_rate": "1.8%",
                "target_scrap_rate": "1.2%",
            },
            "recommendations": [
                "Focus on dimensional tolerance defects, currently 62% of scrap",
                "Review first-pass yield after the last tool change",
                "Escalate if scrap remains above target for the next 2 hours",
            ],
        },
    },
    {
        "keywords": ["handover", "shift handover", "handoff", "next shift"],
        "response": {
            "title": "Shift Handover Status",
            "answer": "Shift handover has 3 equipment alerts pending, 14 open work orders, and one quality hold on Batch #4471.",
            "source": "MES + Maintenance Handover Log",
            "metrics": {
                "equipment_alerts": 3,
                "open_work_orders": 14,
                "quality_holds": 1,
                "staffing": "24 of 26 planned operators",
            },
            "recommendations": [
                "Brief night shift on CNC Unit 7 vibration trend",
                "Keep Batch #4471 on hold until quality inspection is closed",
                "Assign one technician to clear high-priority open work orders first",
            ],
        },
    },
    {
        "keywords": ["downtime", "bottleneck", "constraint", "slowest", "loss"],
        "response": {
            "title": "Downtime and Bottleneck Analysis",
            "answer": "Line 5 is the current bottleneck. Availability is 84.7%, and downtime is driven by repeated feeder resets and maintenance watch events.",
            "source": "Production Analytics - Downtime Pareto",
            "metrics": {
                "bottleneck_line": "LINE-5",
                "availability": "84.7%",
                "top_loss": "feeder resets",
            },
            "recommendations": [
                "Prioritize feeder reset root-cause review on Line 5",
                "Check whether maintenance alerts correlate with throughput dips",
                "Move flexible operators to Line 5 until the bottleneck clears",
            ],
        },
    },
]

FALLBACK = {
    "title": "Manufacturing Assistant",
    "answer": "I can answer manufacturing questions about OEE, production KPIs, maintenance alerts, shift handover, downtime, bottlenecks, and scrap trends.",
    "source": "Sovra Analytics Demo Dataset",
    "metrics": {
        "plant_oee": "78.4%",
        "parts_per_hour": 231,
        "active_alerts": 3,
    },
    "recommendations": [
        "Ask: What is the OEE for Line 3?",
        "Ask: Are there any maintenance alerts for today?",
        "Ask: Give me the current shift production summary",
        "Ask: Which line is causing the most downtime?",
    ],
}


def match(question: str) -> dict:
    q = question.lower()
    best, top = None, 0
    for item in KB:
        score = sum(1 for k in item["keywords"] if k in q)
        if score > top:
            top, best = score, item["response"]
    return best or FALLBACK


@router.get("/snapshot")
def snapshot():
    return PLANT_SNAPSHOT


@router.post("/analyze")
def analyze():
    """Compatibility endpoint for older demos. Returns plant KPI snapshot, not CV defects."""
    return {
        "analysis_type": "manufacturing_kpi_snapshot",
        "snapshot": PLANT_SNAPSHOT,
        "message": "Smart Manufacturing is KPI and operations focused. Defect image analysis belongs to Sovra Vision.",
    }


@router.post("/ask")
def ask(payload: Question):
    result = match(payload.question)
    return {
        **result,
        "site": payload.site,
        "line_id": payload.line_id,
    }
