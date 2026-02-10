import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./Chat.css";

function Chat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading]);

  const sendQuestion = async () => {
    if (!question.trim()) return;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        { role: "ai", text: data.answer },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "ai", text: "⚠️ Error getting response" },
      ]);
    }

    setLoading(false);
  };

  return (
    <div>
      <h3>💬 Chat</h3>

      <div className="chat-container">
        {messages.map((msg, i) => (
          <div
            key={i}
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
        ))}

        {loading && (
          <div className="chat-bubble chat-ai">
            <em>AI is thinking...</em>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
        />
        <button onClick={sendQuestion} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}

export default Chat;
