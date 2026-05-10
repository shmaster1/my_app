import { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send, Bot, User } from "lucide-react";
import { api, getUserIdFromToken } from "../lib/api";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState(() => {
    if (typeof window === "undefined") return [];
    const userId = getUserIdFromToken();
    const key = `chat_history_${userId ?? "guest"}`;
    try {
      return JSON.parse(localStorage.getItem(key)) ?? [];
    } catch {
      return [];
    }
  });
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    const userId = getUserIdFromToken();
    const key = `chat_history_${userId ?? "guest"}`;
    localStorage.setItem(key, JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userId = getUserIdFromToken();
    if (!userId) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);

    try {
      const raw = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/ragchat/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("jwt_token")}`,
          },
          body: JSON.stringify({ user_id: userId, user_text: text, history: messages.slice(-10) }),
        }
      );
      const data = await raw.json();
      let reply;
      if (typeof data === "string") {
        reply = data;
      } else if (data?.type === "product_recommendation") {
        const lines = [data.answer, ...data.products.map((p) => `• ${p.name} — $${p.price}`)];
        reply = lines.join("\n");
      } else {
        reply = (data?.response ?? data?.detail ?? JSON.stringify(data));
      }
      reply = reply.replace(/\\n/g, "\n");
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Connection error. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="fixed top-20 right-6 z-50 flex flex-col items-end gap-3">
      {/* Chat panel */}
      {open && (
        <div className="w-80 h-[480px] bg-white border border-mist rounded-2xl shadow-2xl flex flex-col overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-ink text-white">
            <div className="flex items-center gap-2">
              <Bot size={16} />
              <span className="text-base font-semibold">Chat Assistant</span>
            </div>
            <button onClick={() => setOpen(false)} className="hover:opacity-70 transition">
              <X size={16} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-3 py-3 space-y-3">
            {messages.length === 0 && (
              <p className="text-xs text-fog text-center mt-6">
                Ask me about your orders, favorites, or store info.
              </p>
            )}
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex items-start gap-2 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
              >
                <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0
                  ${msg.role === "user" ? "bg-ink text-white" : "bg-ash text-accent"}`}
                >
                  {msg.role === "user" ? <User size={12} /> : <Bot size={12} />}
                </div>
                <div
                  className={`max-w-[75%] text-sm px-3 py-2 rounded-xl whitespace-pre-wrap
                    ${msg.role === "user"
                      ? "bg-ink text-white rounded-tr-none"
                      : "bg-ash text-ink rounded-tl-none"
                    }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex items-start gap-2">
                <div className="w-6 h-6 rounded-full bg-ash text-accent flex items-center justify-center shrink-0">
                  <Bot size={12} />
                </div>
                <div className="bg-ash text-fog text-sm px-3 py-2 rounded-xl rounded-tl-none">
                  Thinking…
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="px-3 py-3 border-t border-mist flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message…"
              disabled={loading}
              className="flex-1 text-sm bg-ash rounded-xl px-3 py-2.5 text-ink placeholder:text-fog
                focus:outline-none focus:ring-2 focus:ring-ink/10 transition disabled:opacity-50"
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              className="w-8 h-8 bg-ink text-white rounded-xl flex items-center justify-center
                hover:opacity-80 transition disabled:opacity-30"
            >
              <Send size={13} />
            </button>
          </div>
        </div>
      )}

      {/* Toggle button */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="w-12 h-12 bg-ink text-white rounded-full shadow-lg flex items-center justify-center
            hover:opacity-80 transition-all"
        >
          <MessageCircle size={20} />
        </button>
      )}
    </div>
  );
}
