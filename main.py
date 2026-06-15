from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import automotive, enterprise, document, manufacturing

app = FastAPI(
    title="Sovra AI — Demo APIs",
    description="Mock backends for Sovra AI demo use cases",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(automotive.router)
app.include_router(enterprise.router)
app.include_router(document.router)
app.include_router(manufacturing.router)


@app.get("/")
def root():
    return {
        "service": "Sovra AI Demo APIs",
        "endpoints": {
            "automotive":    "POST /automotive/ask",
            "enterprise":    "POST /enterprise/upload  ->  POST /enterprise/ask",
            "document":      "POST /document/upload  →  POST /document/ask",
            "manufacturing": "GET /manufacturing/snapshot  ->  POST /manufacturing/ask",
        },
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Sovra AI Demo APIs",
        "modules": ["automotive", "enterprise", "document", "manufacturing"],
    }
