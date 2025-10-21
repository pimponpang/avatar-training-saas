
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import session, score

app = FastAPI(title="Avatar Training SaaS (Azure TTS)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router, prefix="/session", tags=["session"])
app.include_router(score.router, prefix="/score", tags=["score"])

@app.get("/health")
def health():
    return {"ok": True}
