from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

router = APIRouter(prefix="/enterprise", tags=["Enterprise Knowledge Assistant"])


class Question(BaseModel):
    question: str
    workspace_id: str = "demo-enterprise-kb"


DOCUMENTS = [
    {
        "filename": "ISO 9001 Quality Manual.pdf",
        "doc_type": "quality_manual",
        "source": "ISO 9001 Quality Manual - Section 10.2",
    },
    {
        "filename": "Employee Handbook 2026.docx",
        "doc_type": "employee_handbook",
        "source": "Employee Handbook 2026 - Section 4.1",
    },
    {
        "filename": "IT Security Policy v3.pdf",
        "doc_type": "security_policy",
        "source": "IT Security Policy v3 - Sections 2.1, 3.2, 5.4",
    },
]

KB = [
    {
        "keywords": ["corrective", "nonconform", "non-conform", "quality manual", "root cause", "iso 9001"],
        "response": {
            "title": "Corrective Action Requirements",
            "answer": "Corrective actions must be proportionate to the nonconformity, documented in the QMS, and verified for effectiveness before closure.",
            "source": "ISO 9001 Quality Manual - Section 10.2",
            "steps": [
                "Record the nonconformity and immediate containment action",
                "Identify the root cause using a structured method such as 5 Whys or fishbone analysis",
                "Assign an owner, due date, and corrective action plan",
                "Verify effectiveness within 30 days",
                "Escalate repeated or high-risk nonconformities to quality engineering",
            ],
        },
    },
    {
        "keywords": ["vacation", "annual leave", "time off", "pto", "days off", "holiday"],
        "response": {
            "title": "Vacation & PTO Policy",
            "answer": "Full-time employees receive 28 vacation days per calendar year. Part-time employees receive a pro-rated allowance.",
            "source": "Employee Handbook 2026 - Section 4.1",
            "steps": [
                "Submit vacation requests at least 2 weeks in advance",
                "Manager approval is required before booking travel",
                "Up to 5 unused days can be carried into the next year",
                "Long absences over 10 working days require HR visibility",
            ],
        },
    },
    {
        "keywords": ["password", "reset", "locked", "account", "login", "access", "mfa"],
        "response": {
            "title": "Password & MFA Policy",
            "answer": "Passwords must have at least 12 characters and MFA is mandatory for remote access and privileged systems.",
            "source": "IT Security Policy v3 - Section 3.2",
            "steps": [
                "Use at least 12 characters with uppercase, lowercase, number, and symbol",
                "Do not reuse passwords across company and personal accounts",
                "Passwords expire every 90 days for privileged users",
                "Accounts lock after 5 failed login attempts",
                "Lost MFA devices must be reported to IT immediately",
            ],
        },
    },
    {
        "keywords": ["security", "it policy", "summarize", "summary", "classification", "incident"],
        "response": {
            "title": "IT Security Policy Summary",
            "answer": "The IT policy focuses on MFA, data classification, encryption, incident reporting, approved software, and annual security training.",
            "source": "IT Security Policy v3 - Executive Summary",
            "steps": [
                "MFA is required for remote access and sensitive systems",
                "Data is classified as Public, Internal, Confidential, or Restricted",
                "Confidential and Restricted data must be encrypted at rest and in transit",
                "Security incidents must be reported within 2 hours",
                "Unapproved software requires IT and security review before use",
            ],
        },
    },
    {
        "keywords": ["expense", "reimburse", "receipt", "purchase", "claim"],
        "response": {
            "title": "Expense Reimbursement",
            "answer": "Business expenses must be submitted with receipts and project codes within 30 days of purchase.",
            "source": "Finance Policy - Expense Management",
            "steps": [
                "Upload the receipt in the company expense portal",
                "Select the correct expense category and project code",
                "Manager approval is required for expenses above 50 EUR",
                "Payments are processed twice per month",
            ],
        },
    },
]

FALLBACK = {
    "title": "Enterprise Knowledge Search",
    "answer": "I can answer questions grounded in the loaded enterprise documents: quality manual, employee handbook, and IT security policy.",
    "source": "Sovra Knowledge Demo Workspace",
    "steps": [
        "Ask about corrective action requirements",
        "Ask about vacation or HR policy",
        "Ask about password, MFA, or IT security rules",
        "Upload a PDF, DOCX, or manual in the demo to simulate a new knowledge base",
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


@router.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    """Mock enterprise document ingestion. Content is not parsed in this demo."""
    uploaded = [
        {
            "filename": file.filename or "uploaded-document",
            "content_type": file.content_type or "application/octet-stream",
            "status": "indexed",
        }
        for file in files
    ]
    return {
        "workspace_id": "demo-enterprise-kb",
        "status": "ready",
        "indexed_documents": uploaded or DOCUMENTS,
        "demo_documents": DOCUMENTS,
        "message": "Documents indexed for demo RAG search.",
    }


@router.get("/documents")
def documents():
    return {
        "workspace_id": "demo-enterprise-kb",
        "documents": DOCUMENTS,
    }


@router.post("/ask")
def ask(payload: Question):
    result = match(payload.question)
    return {
        **result,
        "workspace_id": payload.workspace_id,
    }
