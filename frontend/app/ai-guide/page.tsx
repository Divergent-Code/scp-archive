"use client";

import { useState, useRef, useEffect } from "react";
import { aiStatus, askAI } from "../../lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function AIGuidePage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Welcome to the SCP Foundation Archive. I am the Archivist AI. Ask me anything about SCPs, Foundation lore, tales, or Groups of Interest. For example, you can ask me to explain an SCP, recommend entries, or guide you through a narrative canon.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [available, setAvailable] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    aiStatus()
      .then((s) => setAvailable(s.available))
      .catch(() => setAvailable(false));
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const res = await askAI(question);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.answer },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I apologize, but I encountered an error processing your request. Please ensure the AI Guide is properly configured.",
        },
      ]);
    }
    setLoading(false);
  };

  return (
    <div>
      <div className="chat-header">
        <h1>SCP ARCHIVIST AI</h1>
        {available ? (
          <p style={{ color: "#00cc44" }}>AI Guide Online</p>
        ) : (
          <p style={{ color: "#888" }}>
            AI Guide not available. Set ANTHROPIC_API_KEY to enable.
          </p>
        )}
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-message ${msg.role}`}>
              {msg.content}
            </div>
          ))}
          {loading && (
            <div className="chat-message assistant">
              <span className="loading">Thinking</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-area">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask about SCP lore, recommendations, narratives..."
            disabled={!available || loading}
          />
          <button
            className="btn btn-primary"
            onClick={handleSend}
            disabled={!available || loading || !input.trim()}
          >
            SEND
          </button>
        </div>
      </div>
    </div>
  );
}