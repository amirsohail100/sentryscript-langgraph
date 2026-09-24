const API_URL = "/api/analyze";
const CIRCUMFERENCE = 2 * Math.PI * 52;

const rawText = document.getElementById("rawText");
const scanBtn = document.getElementById("scanBtn");
const scanBtnLabel = document.getElementById("scanBtnLabel");
const errorMsg = document.getElementById("errorMsg");
const verdict = document.getElementById("verdict");

const metrics = [
  { key: "toxicity_level", el: document.querySelector('[data-metric="toxicity"]') },
  { key: "copyright_risk", el: document.querySelector('[data-metric="copyright"]') },
  { key: "culture_insensitivity", el: document.querySelector('[data-metric="culture"]') },
];

function bandFor(score) {
  if (score >= 67) return { label: "High risk", color: "var(--danger)" };
  if (score >= 34) return { label: "Medium risk", color: "var(--warn)" };
  return { label: "Low risk", color: "var(--accent)" };
}

function resetGauges() {
  metrics.forEach(({ el }) => {
    const arc = el.querySelector(".arc");
    arc.style.strokeDashoffset = CIRCUMFERENCE;
    arc.style.stroke = "var(--muted)";
    el.querySelector(".gauge-score").textContent = "--";
    el.querySelector(".gauge-status").textContent = "Scanning...";
  });
  errorMsg.textContent = "";
  verdict.textContent = "";
}

function setBusy(isBusy) {
  scanBtn.disabled = isBusy;
  scanBtnLabel.textContent = isBusy ? "Scanning..." : "Run scan";
}

function paintGauge({ el }, score) {
  const arc = el.querySelector(".arc");
  const { label, color } = bandFor(score);
  arc.style.strokeDashoffset = CIRCUMFERENCE * (1 - score / 100);
  arc.style.stroke = color;
  el.querySelector(".gauge-score").textContent = score;
  el.querySelector(".gauge-status").textContent = label;
}

async function scan() {
  const text = rawText.value.trim();
  if (!text) {
    errorMsg.textContent = "Pehle kuch text likho.";
    return;
  }

  resetGauges();
  setBusy(true);

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw_text: text }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);

    metrics.forEach((m) => paintGauge(m, data[m.key]));

    const maxScore = Math.max(data.toxicity_level, data.copyright_risk, data.culture_insensitivity);
    const overall = bandFor(maxScore);
    verdict.textContent = `Overall: ${overall.label} (highest score ${maxScore}/100)`;
  } catch (err) {
    errorMsg.textContent = `Error: ${err.message}`;
  } finally {
    setBusy(false);
  }
}

scanBtn.addEventListener("click", scan);
