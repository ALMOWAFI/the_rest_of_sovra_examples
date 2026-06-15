from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/automotive", tags=["Automotive Assistant"])


class Question(BaseModel):
    question: str


KB = [
    {
        "keywords": ["lane assist", "lane keeping", "lane departure", "lda", "lka"],
        "response": {
            "title": "Enable Lane Assist",
            "answer": "Lane Assist can be enabled from the driver assistance menu when road markings are visible and the vehicle is above the minimum activation speed.",
            "source": "Driving Assistance Manual - Lane Keeping Assist",
            "urgency": "FEATURE GUIDANCE",
            "urgency_level": "info",
            "steps": [
                "Open Vehicle Settings on the center display",
                "Select Driver Assistance",
                "Open Lane Assist or Lane Departure Warning",
                "Switch the feature on and choose the preferred steering or warning sensitivity",
                "Confirm the lane icon appears in the instrument cluster before relying on the feature",
            ],
        },
    },
    {
        "keywords": ["ev charging", "charge ev", "charge the ev", "battery to 80", "charging to 80", "electric charging"],
        "response": {
            "title": "EV Charging Guidance",
            "answer": "For daily driving, charging to around 80% is recommended to reduce battery stress while keeping enough range for most trips.",
            "source": "Electric Drive Manual - Charging Recommendations",
            "urgency": "NORMAL",
            "urgency_level": "low",
            "steps": [
                "Use DC fast charging when you need a quick stop; 10% to 80% typically takes about 35 minutes",
                "Use an 11 kW AC wallbox for overnight charging; 10% to 80% typically takes about 5 to 6.5 hours",
                "Set the charge limit to 80% for daily use",
                "Use 100% only before long trips, then drive soon after charging completes",
            ],
        },
    },
    {
        "keywords": ["tire", "tyre", "pressure", "flat", "tpms", "psi"],
        "response": {
            "title": "Tire Pressure Warning",
            "answer": "One or more tires may be under-inflated. Continue only after checking the tires if the warning persists or handling feels abnormal.",
            "source": "Vehicle Owner Manual - Tire Pressure Monitoring",
            "urgency": "CHECK TODAY",
            "urgency_level": "low",
            "steps": [
                "Stop in a safe location and inspect all four tires visually",
                "Check tire pressure with a gauge when the tires are cold",
                "Inflate to the value on the driver-door label",
                "Reset TPMS from Vehicle Settings after correcting the pressure",
                "If one tire keeps losing pressure, inspect for punctures before driving long distance",
            ],
        },
    },
    {
        "keywords": ["parking sensor", "park sensor", "pdc", "beeping", "parking beep", "sensor beeping"],
        "response": {
            "title": "Parking Sensor Beeping",
            "answer": "Continuous parking sensor warnings are usually caused by a nearby object, dirt on the sensors, ice, rain interference, or a sensor fault.",
            "source": "Parking Assistance Manual - PDC Diagnostics",
            "urgency": "INSPECT SOON",
            "urgency_level": "medium",
            "steps": [
                "Check the area around the vehicle before moving",
                "Clean the parking sensors with water and a soft cloth",
                "Restart the vehicle and test the system at low speed",
                "If beeping continues with no obstacle nearby, schedule service diagnostics",
            ],
        },
    },
    {
        "keywords": ["adaptive cruise", "acc", "cruise control", "following distance"],
        "response": {
            "title": "Adaptive Cruise Control",
            "answer": "Adaptive Cruise Control keeps a selected speed and adjusts following distance when traffic ahead is detected.",
            "source": "Driving Assistance Manual - Adaptive Cruise Control",
            "urgency": "FEATURE GUIDANCE",
            "urgency_level": "info",
            "steps": [
                "Press the cruise control button on the steering wheel",
                "Use Set to store the current speed",
                "Adjust speed with the plus and minus controls",
                "Use the distance button to choose the following gap",
                "Keep hands on the wheel and be ready to brake; the system is driver assistance, not autonomous driving",
            ],
        },
    },
    {
        "keywords": ["oil", "oil pressure", "oil can", "oil light"],
        "response": {
            "title": "Oil Pressure Warning",
            "answer": "Your engine oil pressure may be critically low. This can cause serious engine damage within minutes.",
            "source": "Vehicle Owner Manual - Warning Lights",
            "urgency": "STOP NOW",
            "urgency_level": "critical",
            "steps": [
                "Pull over immediately and turn off the engine",
                "Do not restart the engine",
                "Check oil level with the dipstick",
                "If oil level is normal, call for assistance because the oil pump or pressure sensor may have failed",
            ],
        },
    },
    {
        "keywords": ["temperature", "overheating", "thermometer", "hot", "steam", "coolant"],
        "response": {
            "title": "Engine Overheating",
            "answer": "Your engine is overheating. Continuing to drive risks permanent engine damage.",
            "source": "Vehicle Owner Manual - Cooling System",
            "urgency": "STOP NOW",
            "urgency_level": "critical",
            "steps": [
                "Pull over safely and turn off the engine",
                "Do not open the radiator cap while hot",
                "Wait at least 30 minutes before checking coolant",
                "Add coolant only when the engine is completely cool",
            ],
        },
    },
    {
        "keywords": ["battery warning", "alternator", "charging system", "12v battery"],
        "response": {
            "title": "Battery / Charging System",
            "answer": "The 12V charging system may have failed. The car may be running on stored battery power only.",
            "source": "Vehicle Owner Manual - Electrical System",
            "urgency": "DRIVE CAREFULLY",
            "urgency_level": "high",
            "steps": [
                "Turn off AC, heated seats, and non-essential electronics",
                "Drive directly to a safe destination or service location",
                "Do not turn the vehicle off until you reach a safe place",
            ],
        },
    },
    {
        "keywords": ["check engine", "engine light", "yellow engine"],
        "response": {
            "title": "Check Engine Light",
            "answer": "The engine management system has detected a fault. Severity depends on whether the light is steady or flashing.",
            "source": "Vehicle Owner Manual - Engine Diagnostics",
            "urgency": "STEADY = THIS WEEK | FLASHING = NOW",
            "urgency_level": "medium",
            "steps": [
                "Steady light: check the fuel cap and schedule a diagnostic scan this week",
                "Flashing light: reduce speed immediately and get checked today",
                "Avoid heavy acceleration until diagnosed",
            ],
        },
    },
]

FALLBACK = {
    "title": "Need More Detail",
    "answer": "I can help with ADAS features, EV charging, tire pressure, parking sensors, warning lights, maintenance, and troubleshooting.",
    "source": "Vehicle Knowledge Base",
    "urgency": "PROVIDE MORE DETAIL",
    "urgency_level": "info",
    "steps": [
        "Describe the warning light color and symbol",
        "Mention the vehicle system involved",
        "Tell me whether the issue happened while parked, driving, charging, or braking",
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
