import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./Chat.css";

const SESSION_KEY = "remai_session_id";
const MESSAGES_KEY = "remai_messages";

const createSessionId = () => {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

function Chat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState(() => {
    try {
      const cached = localStorage.getItem(MESSAGES_KEY);
      return cached ? JSON.parse(cached) : [];
    } catch {
      return [];
    }
  });
  const [loading, setLoading] = useState(false);
  const sessionIdRef = useRef(localStorage.getItem(SESSION_KEY) || createSessionId());

  const messagesEndRef = useRef(null);

  useEffect(() => {
    localStorage.setItem(SESSION_KEY, sessionIdRef.current);
  }, []);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading]);

  useEffect(() => {
    localStorage.setItem(MESSAGES_KEY, JSON.stringify(messages));
  }, [messages]);

  const clearChat = async () => {
    const previousSessionId = sessionIdRef.current;

    try {
      await fetch(`http://localhost:8000/chat/session/${previousSessionId}`, {
        method: "DELETE",
      });
    } catch {
      // Best-effort clear: local reset should still happen even if backend is unavailable.
    }

    const nextSessionId = createSessionId();
    sessionIdRef.current = nextSessionId;

    setMessages([]);
    setQuestion("");

    localStorage.setItem(SESSION_KEY, nextSessionId);
    localStorage.setItem(MESSAGES_KEY, JSON.stringify([]));
  };

  const sendQuestion = async () => {
    if (!question.trim()) return;

    const userQuestion = question;
    const historyPayload = messages.slice(-8).map((msg) => ({
      role: msg.role === "ai" ? "assistant" : "user",
      text: msg.text,
    }));

    setMessages((prev) => [...prev, { role: "user", text: userQuestion }]);
    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: userQuestion,
          session_id: sessionIdRef.current,
          history: historyPayload,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.session_id && data.session_id !== sessionIdRef.current) {
        sessionIdRef.current = data.session_id;
        localStorage.setItem(SESSION_KEY, data.session_id);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          text: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (error) {
      const errorMsg =
        error instanceof Error ? error.message : "Unknown error occurred";
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          text: `⚠️ Error: Could not get response. ${errorMsg}`,
        },
      ]);
    }

    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey && !loading) {
      e.preventDefault();
      sendQuestion();
    }
  };

  return (
    <div className="chat-section">
      <div className="chat-header">
        <h3>💬 Chat</h3>
        <button
          type="button"
          className="clear-chat-button"
          onClick={clearChat}
          disabled={loading}
        >
          Clear Chat
        </button>
      </div>

      <div className="chat-container">
        {messages.map((msg, i) => (
          <div key={i}>
            <div
              className={`chat-bubble ${
                msg.role === "user" ? "chat-user" : "chat-ai"
              }`}
            >
              {msg.role === "ai" ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.text}
                </ReactMarkdown>
              ) : (
                msg.text
              )}
            </div>
            {msg.sources && msg.sources.length > 0 && (
              <div className="sources">
                <small>
                  📚 Sources:{" "}
                  {msg.sources
                    .map(
                      (s, idx) =>
                        `${s.source_file} (chunk ${s.chunk_index})`
                    )
                    .join(", ")}
                </small>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="chat-bubble chat-ai">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question... (Press Enter to send)"
          disabled={loading}
          className="chat-input"
        />
        <button
          onClick={sendQuestion}
          disabled={loading}
          className="send-button"
        >
          {loading ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default Chat;
