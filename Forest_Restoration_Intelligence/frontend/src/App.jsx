import { useRef, useState } from "react";
import { analyzeStructured, getChainEvidence, sendChatMessage } from "./api.js";
import ChainResultView from "./components/ChainResultView.jsx";
import ChatInput from "./components/ChatInput.jsx";
import HeroChainPreview from "./components/HeroChainPreview.jsx";
import StructuredForm from "./components/StructuredForm.jsx";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);

  const scrollToBottom = () => {
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
  };

  const handleChainResult = async (response) => {
    setSessionId(response.session_id);

    if (response.type === "clarifying_question") {
      setMessages((m) => [
        ...m,
        { role: "assistant", kind: "clarifying", content: response.message },
      ]);
      return;
    }

    let evidence = null;
    try {
      evidence = await getChainEvidence(response.result.result_id);
    } catch (e) {
      // Non-fatal — the chain result still renders without expanded citations.
      evidence = null;
    }

    setMessages((m) => [
      ...m,
      { role: "assistant", kind: "chain_result", result: response.result, evidence },
    ]);
  };

  const runRequest = async (fn) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fn();
      await handleChainResult(response);
    } catch (e) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
      scrollToBottom();
    }
  };

  const onSendChat = (text) => {
    setMessages((m) => [...m, { role: "user", kind: "text", content: text }]);
    scrollToBottom();
    runRequest(() => sendChatMessage(text, sessionId));
  };

  const onSubmitStructured = (payload) => {
    setMessages((m) => [
      ...m,
      { role: "user", kind: "structured", content: payload },
    ]);
    scrollToBottom();
    runRequest(() => analyzeStructured(payload, sessionId));
  };

  return (
    <div className="app-shell">
      <section className="hero">
        <div className="hero-glow" />
        <div className="hero-content">
          <div className="hero-text">
            <span className="hero-kicker">Causal reasoning for forest restoration</span>
            <h1>Forest Restoration Intelligence</h1>
            <p>
              Describe a degraded forest area — deforestation, rainfall/temperature
              trends, and optionally a region or geo-coordinates — and it traces the
              causal chain from disturbance to biodiversity decline, then recommends
              evidence-backed restoration strategies for the link that broke.
            </p>
          </div>
          <HeroChainPreview />
        </div>
      </section>

      <main className="chat-area">
        {messages.length === 0 && !loading && (
          <p className="empty-hint">
            Try: "A forest area has experienced deforestation. Rainfall has decreased
            and average temperature has increased."
          </p>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message-row ${msg.role}`}>
            {msg.kind === "clarifying" ? (
              <div className="clarifying-block">
                <span className="clarifying-mark">?</span>
                <p>
                  <span className="clarifying-label">Needs more input</span>
                  {msg.content}
                </p>
              </div>
            ) : (
              <div className="message-bubble">
                {msg.kind === "text" && <p>{msg.content}</p>}
                {msg.kind === "structured" && (
                  <pre className="structured-echo">{JSON.stringify(msg.content, null, 2)}</pre>
                )}
                {msg.kind === "chain_result" && (
                  <ChainResultView result={msg.result} evidence={msg.evidence} />
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="message-row assistant">
            <div className="message-bubble">
              <p className="thinking">Reasoning through the causal chain…</p>
            </div>
          </div>
        )}
        {error && <div className="error-banner">Error: {error}</div>}
        <div ref={bottomRef} />
      </main>

      <footer className="app-footer">
        <ChatInput onSend={onSendChat} disabled={loading} />
        <StructuredForm onSubmit={onSubmitStructured} disabled={loading} />
      </footer>
    </div>
  );
}
