import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

// npm run dev -> local backend, npm run build (Render) -> production backend
// Render-la backend deploy aanadhum, keezha irukkura URL-ah maathunga
const BACKEND_URL = import.meta.env.DEV
  ? "http://localhost:8000"
  : "https://rag-chatbot-api.onrender.com";

const SUGGESTIONS = [
  "What skills does Yasir know?",
  "Tell me about Yasir's projects",
  "Where did Yasir study?",
  "How can I contact Yasir?",
];

const WELCOME = {
  role: "bot",
  text: "Hi 👋 I'm Yasir's resume assistant. Ask me anything about his skills, projects, education or experience.",
};

function App() {
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  // Pudhu message vandhaa keezha scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (question) => {
    const text = question.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${BACKEND_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Something went wrong");
      setMessages((prev) => [...prev, { role: "bot", text: data.answer, sources: data.sources }]);
    } catch (err) {
      const msg = err.message === "Failed to fetch" ? "Can't reach the server. It may be starting up, try again in a few seconds" : err.message;
      setMessages((prev) => [...prev, { role: "bot", text: `⚠️ ${msg}`, error: true }]);
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const showSuggestions = messages.length === 1;

  return (
    <div className="app">
      <header className="header">
        <div className="avatar">🤖</div>
        <div>
          <h1>Resume Chatbot</h1>
          <p className="status">
            <span className="dot" /> RAG · Groq · pgvector
          </p>
        </div>
      </header>

      <main className="chat">
        {messages.map((m, i) => (
          <div key={i} className={`row ${m.role}`}>
            {m.role === "bot" && <div className="mini-avatar">🤖</div>}
            <div className={`bubble ${m.role} ${m.error ? "error" : ""}`}>
              {m.role === "bot" ? <ReactMarkdown>{m.text}</ReactMarkdown> : m.text}

              {m.sources?.length > 0 && (
                <details className="sources">
                  <summary>📄 Sources ({m.sources.length})</summary>
                  {m.sources.map((s, j) => (
                    <div key={j} className="source">
                      <span className="score">{Math.round(s.score * 100)}% match</span>
                      <p>{s.text}</p>
                    </div>
                  ))}
                </details>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="row bot">
            <div className="mini-avatar">🤖</div>
            <div className="bubble bot typing">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}

        {showSuggestions && (
          <div className="suggestions">
            {SUGGESTIONS.map((s) => (
              <button key={s} type="button" onClick={() => sendMessage(s)}>
                {s}
              </button>
            ))}
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      <form className="composer" onSubmit={onSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about Yasir's resume..."
          maxLength={500}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()} aria-label="Send">
          ➤
        </button>
      </form>
    </div>
  );
}

export default App;
