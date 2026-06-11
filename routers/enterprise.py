from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/enterprise", tags=["Enterprise Knowledge Assistant"])


class Question(BaseModel):
    question: str


KB = [
    {
        "keywords": ["expense", "reimburse", "receipt", "purchase", "claim"],
        "response": {
            "title": "Expense Reimbursement",
            "answer": "All business expenses must be submitted within 30 days of purchase.",
            "source": "HR Policy Manual — Section 4.2",
            "steps": [
                "Log in to the company portal at expenses.company.com",
                "Upload receipt and fill in the expense category and project code",
                "Under $50: auto-approved within 24 hours",
                "$50–$500: requires direct manager approval (1–2 business days)",
                "Over $500: requires department head approval (3–5 business days)",
                "Payment processed on the 15th and last day of each month",
            ],
        },
    },
    {
        "keywords": ["vacation", "annual leave", "time off", "pto", "days off", "holiday"],
        "response": {
            "title": "Vacation & PTO Policy",
            "answer": "Full-time employees receive 20 days of paid time off per year, accrued monthly.",
            "source": "HR Policy Manual — Section 2.1",
            "steps": [
                "Accrue 1.67 days per month (resets January 1)",
                "Request time off at least 2 weeks in advance for periods over 3 days",
                "Submit requests via the HR portal under Leave Requests",
                "Up to 5 unused days can be carried over to the next year",
            ],
        },
    },
    {
        "keywords": ["password", "reset", "locked", "account", "login", "access", "mfa"],
        "response": {
            "title": "Password Reset & Account Access",
            "answer": "Account issues are handled by the IT Helpdesk. Most resets complete within 15 minutes.",
            "source": "IT Policy — Section 1.4",
            "steps": [
                "Self-service reset: visit sso.company.com and click Forgot Password",
                "If self-service fails: contact IT at it@company.com or ext. 1001",
                "Slack #it-support for faster response during business hours",
                "Lost MFA device: visit IT desk in person with your employee ID",
            ],
        },
    },
    {
        "keywords": ["remote", "work from home", "wfh", "hybrid", "office days"],
        "response": {
            "title": "Remote Work Policy",
            "answer": "The company operates on a hybrid model. Teams set their own in-office schedules.",
            "source": "HR Policy Manual — Section 3.5",
            "steps": [
                "Minimum 2 days per week in-office (Tuesday and Thursday recommended)",
                "Remote equipment budget: $800 one-time, request via IT portal",
                "VPN required for all remote access to internal systems",
                "Core hours: 10am–3pm local time regardless of location",
                "International remote work 30+ days: requires HR and legal approval",
            ],
        },
    },
    {
        "keywords": ["onboarding", "new hire", "first day", "start", "joining"],
        "response": {
            "title": "New Employee Onboarding",
            "answer": "Onboarding spans your first two weeks and is structured by HR.",
            "source": "Onboarding Guide v3.2",
            "steps": [
                "Day 1: IT setup, badge, HR paperwork — report to reception at 9am",
                "Week 1: complete all mandatory compliance training in the Learning Portal",
                "Week 1: schedule 1:1s with your direct team members",
                "Week 2: complete department-specific tool training",
                "30/60/90 day check-ins are scheduled automatically by HR",
            ],
        },
    },
    {
        "keywords": ["benefit", "insurance", "health", "dental", "401k", "pension", "equity", "stock"],
        "response": {
            "title": "Employee Benefits",
            "answer": "Full benefits are available to all full-time employees from Day 1.",
            "source": "Benefits Guide 2024",
            "steps": [
                "Health insurance: choose plan during first 30 days at benefits.company.com",
                "Dental & vision: included in all health plans at no extra cost",
                "401(k): company matches up to 4% — enroll via Fidelity portal",
                "Life insurance: 2x annual salary, automatic enrollment",
                "Equity/RSU: 4-year vesting schedule, 1-year cliff — see offer letter",
            ],
        },
    },
    {
        "keywords": ["compliance", "code of conduct", "ethics", "harassment", "conflict"],
        "response": {
            "title": "Compliance & Code of Conduct",
            "answer": "All employees must complete annual compliance training by December 31.",
            "source": "Code of Conduct 2024 — Section 1",
            "steps": [
                "Anti-harassment: zero tolerance — report via hr@company.com or EthicsPoint anonymously",
                "Conflict of interest: disclose outside business relationships to manager and HR",
                "Confidentiality: all internal data is confidential — no external sharing without approval",
                "Social media: do not speak on behalf of the company publicly",
            ],
        },
    },
    {
        "keywords": ["payroll", "salary", "pay", "paycheck", "payslip", "compensation"],
        "response": {
            "title": "Payroll Information",
            "answer": "Salaries are paid bi-weekly on Fridays.",
            "source": "Payroll Policy — Section 2",
            "steps": [
                "Pay date: every other Friday — see payroll calendar on HR portal",
                "Payslips available in Workday under Pay, 2 days before pay date",
                "Direct deposit changes: submit at least 5 business days before next pay date",
                "Tax forms (W-2): available by January 31 each year",
                "Discrepancies: contact payroll@company.com",
            ],
        },
    },
    {
        "keywords": ["training", "learning", "course", "certification", "development", "upskill", "budget"],
        "response": {
            "title": "Learning & Development",
            "answer": "The company supports continuous learning with a dedicated annual budget.",
            "source": "L&D Policy — Section 5",
            "steps": [
                "Annual L&D budget: $1,500 per employee (resets January 1)",
                "Pre-approved training: any course on the internal catalog — instant approval",
                "External certifications: submit request to manager with cost and business justification",
                "Study time: up to 2 hours/week during work hours with manager approval",
            ],
        },
    },
    {
        "keywords": ["it", "laptop", "equipment", "hardware", "software", "tool", "request", "ticket"],
        "response": {
            "title": "IT Equipment & Software",
            "answer": "IT requests are processed within 2 business days for standard items.",
            "source": "IT Policy — Section 2.1",
            "steps": [
                "New software request: submit ticket at it.company.com/requests",
                "Hardware issue: same-day response for critical failures",
                "Loaner equipment: available from IT desk for up to 2 weeks",
                "Approved software list: on the IT portal — unlisted software requires security review",
            ],
        },
    },
]

FALLBACK = {
    "title": "Let Me Check That",
    "answer": "I can help with HR policies, IT support, compliance, payroll, benefits, and internal procedures. Try rephrasing with more specific keywords.",
    "source": "General Reference",
    "steps": [
        "Browse the full policy library at policy.company.com",
        "For urgent HR matters: hr@company.com",
        "For IT issues: it@company.com or Slack #it-support",
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
