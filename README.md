# SentryScript-LangGraph

SentryScript is a parallel LangGraph pipeline that fans a script out to three independent AI checks — toxicity and hate speech, copyright and originality risk, and cultural sensitivity — then merges the scores into one safety dashboard. Built with FastAPI, Groq, and a lightweight HTML/CSS/JS UI.

Iska pichle `ScriptFlow-LangGraph` project se farak sirf ye hai: wahan pe stages **sequential** the (editor → scriptwriter → translator), yahan teeno checks `START` se hi **parallel** fire hote hain aur `AnalyzerState` ka `merge_score_dicts` reducer unke partial results ko ek dict me combine kar deta hai.

## Structure

```
SentryScript-LangGraph/
├── main.py            # FastAPI app: /api/analyze, /api/health, serves the UI
├── agent.py            # Graph wiring: START -> {toxicity, copyright, culture} -> END
├── schema/
│   └── payload.py      # AnalyzeRequest / AnalyzeResponse
├── state/
│   └── AnalyzerState.py  # AnalyzerState + merge_score_dicts reducer
├── tools/
│   └── nodes.py         # 3 node functions, each an independent Groq call
├── static/
│   ├── index.html
│   ├── style.css
│   └── script.js         # 3 radial gauges + overall verdict
├── requirements.txt
└── .env                  # GROQ_API_KEY yahan daalo (git me commit mat karna)
```

## Endpoints

- `GET  /api/health` → `{"status": "ok"}`
- `POST /api/analyze` → body `{"raw_text": "..."}`, returns:
  ```json
  {
    "toxicity_level": 0,
    "copyright_risk": 0,
    "culture_insensitivity": 0
  }
  ```
  Rate limited to **5 requests/minute per IP** (slowapi) — kyunki har call 3 parallel Groq requests fire karti hai.
- `GET  /` → dashboard UI (`static/index.html`)

## Run locally

```bash
pip install -r requirements.txt
# .env me GROQ_API_KEY=your_key daalo
uvicorn main:app --reload --port 8000
```

Browser me `http://localhost:8000` kholo.

## Score reading

- `0–33` → Low risk (green)
- `34–66` → Medium risk (amber)
- `67–100` → High risk (red)

## Before going to production

- CORS abhi `allow_origins=["*"]` par hai — apne actual frontend domain tak restrict kar dena.
- Rate limit (`5/minute`) apni expected traffic ke hisaab se tune kar lena.
- `GROQ_API_KEY` startup pe validate nahi hoti — missing hone par pehli request pe hi 502 milega. Chaho to `main.py` me ek startup check add kar sakte ho.
