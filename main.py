import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from schema.payload import AnalyzeRequest, AnalyzeResponse
from agent import run_analysis

app = FastAPI(title="SentryScript Safety Analyzer API")

# Rate limiting: IP address ke hisaab se limit lagayi hai, kyunki har call 3x Groq
# API ko hit karti hai (teeno branches parallel me). Traffic ke hisaab se tune kar lena.
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Dev ke time frontend alag origin se call kar sake, isliye CORS open rakha hai.
# Production me isko apne actual frontend domain tak restrict kar dena.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# 5 requests per minute, per IP.
@app.post("/api/analyze", response_model=AnalyzeResponse)
@limiter.limit("5/minute")
def analyze(request: Request, payload: AnalyzeRequest):
    if not payload.raw_text.strip():
        raise HTTPException(status_code=400, detail="raw_text khaali hai")

    try:
        scores = run_analysis(payload.raw_text)
    except Exception as exc:  # Groq API errors, network issues, etc.
        raise HTTPException(status_code=502, detail=str(exc))

    return AnalyzeResponse(
        toxicity_level=scores.get("toxicity_level", 0),
        copyright_risk=scores.get("copyright_risk", 0),
        culture_insensitivity=scores.get("culture_insensitivity", 0),
    )


# Frontend (index.html/style.css/script.js) ko isi FastAPI server se serve karo.
# __file__ ke absolute path se STATIC_DIR nikala hai taaki app kisi bhi
# working directory se start ho, path hamesha sahi resolve ho.
# Ye line hamesha sabse aakhir me honi chahiye, kyunki ye "/" ko catch-all bana deti hai.
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
