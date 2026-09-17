const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function post(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json();
}

async function get(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json();
}

export function sendChatMessage(message, sessionId) {
  return post("/chat", { message, session_id: sessionId ?? null });
}

export function analyzeStructured(payload, sessionId) {
  return post("/analyze", { ...payload, session_id: sessionId ?? null });
}

export function getSession(sessionId) {
  return get(`/session/${sessionId}`);
}

export function getChainEvidence(resultId) {
  return get(`/chain-evidence/${resultId}`);
}
