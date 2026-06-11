from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/automotive", tags=["Automotive Assistant"])


class Question(BaseModel):
    question: str


KB = [
    {
        "keywords": ["oil", "oil pressure", "oil can", "oil light"],
        "response": {
            "title": "Oil Pressure Warning",
            "answer": "Your engine oil pressure is critically low. This can cause serious engine damage within minutes.",
            "urgency": "STOP NOW",
            "urgency_level": "critical",
            "steps": [
                "Pull over immediately and turn off the engine",
                "Do NOT restart the engine",
                "Check oil level with the dipstick",
                "If oil level is normal, call for assistance — possible pump failure",
            ],
        },
    },
    {
        "keywords": ["temperature", "overheating", "thermometer", "hot", "steam", "coolant"],
        "response": {
            "title": "Engine Overheating",
            "answer": "Your engine is overheating. Continuing to drive risks permanent engine damage.",
            "urgency": "STOP NOW",
            "urgency_level": "critical",
            "steps": [
                "Pull over safely and turn off the engine",
                "Do NOT open the radiator cap while hot",
                "Wait at least 30 minutes before checking coolant",
                "Add coolant only when the engine is completely cool",
            ],
        },
    },
    {
        "keywords": ["battery", "charging", "alternator"],
        "response": {
            "title": "Battery / Charging System",
            "answer": "Your charging system has failed. The car is running on battery power only.",
            "urgency": "DRIVE CAREFULLY",
            "urgency_level": "high",
            "steps": [
                "Turn off AC, radio, and all non-essential electronics",
                "Drive directly home or to a shop — you may have 20–40 minutes",
                "Do not turn the engine off until you reach a safe destination",
            ],
        },
    },
    {
        "keywords": ["brake", "braking", "brake light", "brake pedal", "spongy"],
        "response": {
            "title": "Brake System Warning",
            "answer": "There may be a brake system fault or low brake fluid.",
            "urgency": "STOP SOON",
            "urgency_level": "high",
            "steps": [
                "Check if the parking brake is fully released",
                "Test brakes gently — if pedal feels soft or sinks, stop driving",
                "Check brake fluid level in the reservoir under the hood",
                "If fluid is low or brakes feel wrong, call for help",
            ],
        },
    },
    {
        "keywords": ["check engine", "engine light", "yellow engine"],
        "response": {
            "title": "Check Engine Light",
            "answer": "The engine management system has detected a fault. Severity depends on whether the light is steady or flashing.",
            "urgency": "STEADY = THIS WEEK  |  FLASHING = NOW",
            "urgency_level": "medium",
            "steps": [
                "Steady light: check the gas cap is tight — if it stays on, get a diagnostic scan this week",
                "Flashing light: reduce speed immediately and get checked today — active engine misfire",
                "Avoid heavy acceleration until diagnosed",
            ],
        },
    },
    {
        "keywords": ["tire", "tyre", "pressure", "flat", "tpms", "psi"],
        "response": {
            "title": "Tire Pressure Warning",
            "answer": "One or more tires are significantly under-inflated (25%+ below recommended).",
            "urgency": "CHECK TODAY",
            "urgency_level": "low",
            "steps": [
                "Check all four tire pressures when safe to stop",
                "Recommended pressure: 32–35 PSI (check door sticker for your car)",
                "Inflate to correct level — light should turn off after a few miles",
                "Inspect for nails or punctures if one tire keeps losing pressure",
            ],
        },
    },
    {
        "keywords": ["noise", "sound", "grinding", "squealing", "clicking", "knocking", "rattling"],
        "response": {
            "title": "Unusual Sound Detected",
            "answer": "Unusual sounds often signal worn components. Location and type of sound identifies the cause.",
            "urgency": "DEPENDS ON SOUND",
            "urgency_level": "medium",
            "steps": [
                "Grinding when braking → worn brake pads, replace soon",
                "Clicking when turning → CV joint issue, inspect within a week",
                "Knocking from engine → low oil or engine knock, check oil immediately",
                "Rattling from underneath → loose heat shield or exhaust, not urgent",
            ],
        },
    },
    {
        "keywords": ["oil change", "maintenance", "service", "maint", "wrench", "schedule"],
        "response": {
            "title": "Maintenance Schedule",
            "answer": "Your vehicle is due for scheduled maintenance.",
            "urgency": "SCHEDULE SOON",
            "urgency_level": "low",
            "steps": [
                "Oil and filter: every 5,000 miles or 6 months",
                "Tire rotation: every 5,000 miles",
                "Brake inspection: every 15,000 miles",
                "Cabin air filter: every 15,000–20,000 miles",
                "To reset maintenance light: hold trip reset button while turning ignition ON",
            ],
        },
    },
    {
        "keywords": ["4wd", "four wheel", "awd", "traction", "vsc", "stability"],
        "response": {
            "title": "Traction / Stability Control",
            "answer": "Your traction or stability control system has been activated or has a fault.",
            "urgency": "INSPECT IF UNPROMPTED",
            "urgency_level": "medium",
            "steps": [
                "If VSC light came on by itself: have the system inspected",
                "If 4WD light is flashing: stop and wait for transfer case to cool",
                "Traction control activating on slippery roads is normal — it is working correctly",
            ],
        },
    },
    {
        "keywords": ["fuel", "gas", "empty", "low fuel", "range"],
        "response": {
            "title": "Low Fuel Warning",
            "answer": "You have approximately 2–3 gallons remaining (roughly 40–60 miles).",
            "urgency": "REFUEL SOON",
            "urgency_level": "low",
            "steps": [
                "Refuel at your earliest convenience",
                "Avoid running completely empty — can damage the fuel pump",
            ],
        },
    },
]

FALLBACK = {
    "title": "Need More Detail",
    "answer": "I can help with warning lights, sounds, smells, maintenance, and vehicle features. Could you describe what you're seeing or hearing in more detail?",
    "urgency": "PROVIDE MORE DETAIL",
    "urgency_level": "info",
    "steps": [
        "Describe the warning light color and symbol shape",
        "Describe any unusual sounds and when they occur",
        "Mention any changes in how the car drives or feels",
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


@router.post("/ask")
def ask(payload: Question):
    return match(payload.question)
