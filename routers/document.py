from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

router = APIRouter(prefix="/document", tags=["Document Intelligence"])


class Question(BaseModel):
    question: str
    doc_type: str = "contract"  # passed back from /upload response


# Mock document profiles keyed by type
PROFILES = {
    "contract": {
        "doc_type": "contract",
        "label": "Service Agreement",
        "pages": 12,
        "word_count": 4820,
        "summary": "A 12-page service agreement between Acme Corp and TechVendor Ltd covering software implementation, support SLAs, and payment terms over a 12-month engagement.",
        "dates": ["Start date: March 1, 2024", "End date: February 28, 2025", "Payment due: Net 30 from invoice date"],
        "parties": ["Acme Corp (Client)", "TechVendor Ltd (Service Provider)"],
        "financial": "$240,000 total contract value — paid in 4 quarterly installments of $60,000",
        "risks": "Late delivery clause: 2% penalty per week beyond agreed milestones. Either party may terminate with 30 days written notice.",
        "obligations": ["TechVendor must deliver Phase 1 by May 1, 2024", "Acme Corp must provide system access within 5 business days of signing", "Monthly status reports required from both parties"],
        "key_clauses": ["Limitation of liability capped at total contract value", "Governing law: State of New York", "Dispute resolution: mediation before arbitration"],
    },
    "invoice": {
        "doc_type": "invoice",
        "label": "Invoice #INV-2024-0847",
        "pages": 2,
        "word_count": 380,
        "summary": "Invoice from DataSystems Inc for Q3 consulting services and software licenses. Total amount due within 30 days.",
        "dates": ["Invoice date: October 1, 2024", "Due date: October 31, 2024", "Service period: July–September 2024"],
        "parties": ["DataSystems Inc (Vendor)", "Your Organization (Client)"],
        "financial": "$18,450 total due — Consulting: $12,000 | Software licenses: $6,450",
        "risks": "Late fees of 1.5% per month apply after due date. Unpaid invoices may result in service suspension.",
        "obligations": ["Payment due by October 31, 2024", "Dispute must be raised within 14 days of invoice date"],
        "key_clauses": ["Net 30 payment terms", "Late fee: 1.5% monthly", "Services rendered per SOW-2024-Q3"],
    },
    "report": {
        "doc_type": "report",
        "label": "Q3 2024 Financial Report",
        "pages": 28,
        "word_count": 11200,
        "summary": "Quarterly financial report covering revenue, expenses, gross margin, and KPIs for the period July 1 – September 30, 2024.",
        "dates": ["Report period: July 1 – September 30, 2024", "Board submission: October 15, 2024", "Next review: Q4 report due January 2025"],
        "parties": ["Finance Department (Author)", "Executive Leadership (Audience)"],
        "financial": "Revenue: $4.2M | EBITDA: $820K | Net margin: 12.4% | YoY growth: +8.3%",
        "risks": "Gross margin declined 2.1% vs Q2. Supply chain costs increased 8% YoY. Two key clients represent 34% of revenue.",
        "obligations": ["Board approval required by October 20, 2024", "Action items assigned to 3 department heads"],
        "key_clauses": ["Confidential — Internal Use Only", "Subject to external audit in Q4", "Forward-looking statements are estimates"],
    },
    "policy": {
        "doc_type": "policy",
        "label": "Company Policy Handbook 2024",
        "pages": 45,
        "word_count": 18600,
        "summary": "Comprehensive company policy handbook covering HR procedures, IT acceptable use, compliance requirements, and operational standards.",
        "dates": ["Effective date: January 1, 2024", "Next review: January 1, 2025", "Remote work update: compliance deadline March 1, 2024"],
        "parties": ["HR Department (Owner)", "All Employees (Subject)"],
        "financial": "L&D budget: $1,500/employee | Equipment budget: $800 one-time",
        "risks": "Section 3.2 updated — remote work now requires minimum 2 days in office. Non-compliance may result in disciplinary action.",
        "obligations": ["Annual compliance training by December 31", "Remote work policy compliance by March 1, 2024", "All employees must acknowledge receipt of handbook"],
        "key_clauses": ["At-will employment", "Mandatory arbitration for disputes", "IP assignment clause covers all work product"],
    },
    "default": {
        "doc_type": "document",
        "label": "Uploaded Document",
        "pages": 8,
        "word_count": 3200,
        "summary": "Document analyzed successfully. Key information, structure, and content have been extracted.",
        "dates": ["Primary date: Q1 2024", "Secondary date: Q3 2024", "Reference date: Q4 2024"],
        "parties": ["Primary party identified", "Secondary party identified"],
        "financial": "Financial references detected — see document for specific amounts",
        "risks": "2 items flagged for review during analysis",
        "obligations": ["Key obligations extracted from document body", "Deadlines identified in sections 2 and 4"],
        "key_clauses": ["Standard terms apply", "Review flagged sections carefully"],
    },
}

KB = [
    {
        "keywords": ["summary", "summarize", "overview", "about", "what is", "tldr", "describe"],
        "handler": lambda p: {
            "title": "Document Summary",
            "answer": p["summary"],
            "items": [f"Type: {p['label']}", f"Length: {p['pages']} pages, ~{p['word_count']:,} words", *p["parties"]],
            "quote": None,
        },
    },
    {
        "keywords": ["date", "dates", "deadline", "when", "timeline", "schedule", "period"],
        "handler": lambda p: {
            "title": "Key Dates",
            "answer": "The following dates were identified in the document:",
            "items": p["dates"],
            "quote": p["dates"][0],
        },
    },
    {
        "keywords": ["party", "parties", "who", "company", "organization", "client", "vendor", "signatory"],
        "handler": lambda p: {
            "title": "Parties Involved",
            "answer": "The document references the following parties:",
            "items": p["parties"],
            "quote": None,
        },
    },
    {
        "keywords": ["value", "amount", "cost", "price", "payment", "fee", "total", "money", "financial", "dollar"],
        "handler": lambda p: {
            "title": "Financial Information",
            "answer": "Key financial details extracted from the document:",
            "items": [p["financial"], *[d for d in p["dates"] if any(w in d.lower() for w in ["pay", "due", "invoice"])]],
            "quote": p["financial"],
        },
    },
    {
        "keywords": ["liability", "limitation of liability", "liability clause"],
        "handler": lambda p: {
            "title": "Liability Clause",
            "answer": "The document limits liability to the contract value unless excluded by law or by specific carve-outs such as fraud, willful misconduct, or data breach obligations.",
            "items": [
                "Liability cap: total contract value",
                "Review carve-outs before signature",
                "Legal review recommended for high-risk or regulated deployments",
            ],
            "quote": "Limitation of liability capped at total contract value",
        },
    },
    {
        "keywords": ["risk", "penalty", "termination", "issue", "concern", "flag", "problem"],
        "handler": lambda p: {
            "title": "Risks & Flagged Items",
            "answer": "The following items were flagged during analysis:",
            "items": [p["risks"]],
            "quote": p["risks"],
        },
    },
    {
        "keywords": ["obligation", "requirement", "must", "shall", "responsible", "duty", "required"],
        "handler": lambda p: {
            "title": "Obligations & Requirements",
            "answer": "Key obligations identified in the document:",
            "items": p["obligations"],
            "quote": None,
        },
    },
    {
        "keywords": ["clause", "term", "condition", "provision", "section", "article"],
        "handler": lambda p: {
            "title": "Key Clauses",
            "answer": "Important clauses and terms extracted from the document:",
            "items": p["key_clauses"],
            "quote": p["key_clauses"][0] if p["key_clauses"] else None,
        },
    },
]

FALLBACK_HANDLER = lambda p: {
    "title": "Document Analysis",
    "answer": f"Based on the {p['label']}, here is the key information:",
    "items": [p["summary"], p["financial"], *p["dates"][:2]],
    "quote": None,
}


def detect_type(filename: str) -> str:
    f = filename.lower()
    if any(w in f for w in ["contract", "agreement", "service", "sow"]):
        return "contract"
    if any(w in f for w in ["invoice", "inv-", "bill", "receipt"]):
        return "invoice"
    if any(w in f for w in ["report", "financial", "q3", "q4", "q1", "q2"]):
        return "report"
    if any(w in f for w in ["policy", "handbook", "hr", "procedure"]):
        return "policy"
    return "default"


def match_question(question: str, profile: dict) -> dict:
    q = question.lower()
    best, top = None, 0
    for item in KB:
        score = sum(1 for k in item["keywords"] if k in q)
        if score > top:
            top, best = score, item["handler"]
    return (best or FALLBACK_HANDLER)(profile)


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    """Upload a document. Returns extracted metadata and doc_type to use in /ask."""
    doc_type = detect_type(file.filename or "document")
    profile = PROFILES[doc_type]
    return {
        "status": "analyzed",
        "document_id": f"demo-{doc_type}",
        "filename": file.filename or profile["label"],
        "content_type": file.content_type or "application/octet-stream",
        "doc_type": doc_type,
        "label": profile["label"],
        "pages": profile["pages"],
        "word_count": profile["word_count"],
        "summary": profile["summary"],
        "dates": profile["dates"],
        "parties": profile["parties"],
        "financial": profile["financial"],
        "risks": profile["risks"],
    }


@router.post("/ask")
def ask(payload: Question):
    """Ask a question about the previously uploaded document. Pass doc_type from /upload."""
    profile = PROFILES.get(payload.doc_type, PROFILES["default"])
    return match_question(payload.question, profile)
