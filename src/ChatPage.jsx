import React, { useEffect, useRef, useState } from "react";

const BACKEND_URL = "http://localhost:8000/chat";

function extractBookCandidates(text) {
  if (!text) return [];
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .filter((line) => line.startsWith("-") || line.startsWith("•"))
    .map((line) => line.replace(/^[-•]\s*/, ""));
}

function ChatPage({ onAddBook, libraryCount }) {
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      role: "assistant",
      content: "Hi, I'm LIRIA. Tell me what kind of book you're looking for.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const chatRef = useRef(null);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input.trim(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setError(null);
    setIsLoading(true);

    try {
      const res = await fetch(BACKEND_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage.content }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      const replyText = data.reply || "I couldn't parse a reply from the server.";

      const aiMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: replyText,
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error(err);
      setError("There was an error communicating with the server.");
      const aiMessage = {
        id: `assistant-error-${Date.now()}`,
        role: "assistant",
        content: "Sorry, I had a server issue. Please try again later.",
      };
      setMessages((prev) => [...prev, aiMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // auto scroll
  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  };

  const lastAssistantMessage = [...messages]
    .reverse()
    .find((m) => m.role === "assistant");
  const candidates = lastAssistantMessage
    ? extractBookCandidates(lastAssistantMessage.content).slice(0, 5)
    : [];

  return (
    <div
      style={{
        padding: "24px 16px 32px",
        display: "flex",
        flexDirection: "column",
        gap: "24px",
        alignItems: "center",
      }}
    >
      {/* HEADER */}
      <header
        style={{
          maxWidth: "1080px",
          width: "100%",
          textAlign: "center",
        }}
      >
        <h1
          style={{
            fontSize: "26px",
            fontWeight: 650,
            marginBottom: "6px",
            letterSpacing: "-0.04em",
            color: "#f9fafb",
            textShadow: "0 18px 45px rgba(15,23,42,0.9)",
          }}
        >
          LIRIA — Chat
        </h1>
        <p
          style={{
            fontSize: "14px",
            lineHeight: 1.6,
            color: "#cbd5f5",
            maxWidth: "560px",
            margin: "0 auto",
          }}
        >
          Describe your mood, your favorite authors, or a recent book. LIRIA will
          suggest titles and help you build your long‑term reading profile.
        </p>
      </header>

      {/* CHAT CARD */}
      <main
        style={{
          maxWidth: "1080px",
          width: "100%",
          display: "grid",
          gridTemplateColumns: "minmax(0, 3fr) minmax(0, 2fr)",
          gap: "18px",
          alignItems: "stretch",
        }}
      >
        <section
          style={{
            background:
              "linear-gradient(135deg, rgba(15,23,42,0.95), rgba(15,23,42,0.9))",
            borderRadius: "20px",
            border: "1px solid rgba(148,163,184,0.25)",
            boxShadow:
              "0 22px 50px rgba(15,23,42,0.9), 0 0 0 1px rgba(15,23,42,0.8) inset",
            padding: "18px 18px 16px",
            display: "flex",
            flexDirection: "column",
            height: "520px",
            backdropFilter: "blur(14px)",
          }}
        >
          <div
            ref={chatRef}
            style={{
              flex: 1,
              overflowY: "auto",
              paddingRight: "6px",
              display: "flex",
              flexDirection: "column",
              gap: "10px",
              marginBottom: "12px",
            }}
          >
            {messages.map((msg) => {
              const isUser = msg.role === "user";
              return (
                <div
                  key={msg.id}
                  style={{
                    display: "flex",
                    justifyContent: isUser ? "flex-end" : "flex-start",
                    gap: "8px",
                  }}
                >
                  {!isUser && (
                    <div
                      style={{
                        width: "28px",
                        height: "28px",
                        borderRadius: "999px",
                        background:
                          "radial-gradient(circle at 30% 20%, #4f46e5 0, #0ea5e9 40%, #020617 75%)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "12px",
                        fontWeight: 600,
                        color: "#e5e7eb",
                        boxShadow: "0 10px 25px rgba(15,23,42,0.9)",
                        flexShrink: 0,
                      }}
                    >
                      L
                    </div>
                  )}
                  <div
                    style={{
                      maxWidth: "80%",
                      padding: "9px 13px",
                      borderRadius: isUser
                        ? "18px 18px 4px 18px"
                        : "18px 18px 18px 4px",
                      fontSize: "14px",
                      backgroundColor: isUser
                        ? "linear-gradient(135deg, rgba(30,64,175,0.4), rgba(15,23,42,0.95))"
                        : "linear-gradient(135deg, rgba(30,64,175,0.25), rgba(15,23,42,0.95))",
                      color: isUser ? "#f9fafb" : "#e5e7eb",
                      border: isUser
                        ? "1px solid rgba(148,163,184,0.45)"
                        : "1px solid rgba(129,140,248,0.45)",
                      boxShadow: isUser
                        ? "0 10px 25px rgba(15,23,42,0.55)"
                        : "0 10px 25px rgba(15,23,42,0.65)",
                      lineHeight: 1.5,
                      whiteSpace: "pre-wrap",
                    }}
                  >
                    {msg.content}
                  </div>
                </div>
              );
            })}
          </div>

          {error && (
            <div
              style={{
                fontSize: "12px",
                color: "#fecaca",
                background:
                  "linear-gradient(135deg, rgba(127,29,29,0.7), rgba(127,29,29,0.4))",
                border: "1px solid rgba(248,113,113,0.8)",
                borderRadius: "6px",
                padding: "4px 8px",
                marginBottom: "6px",
              }}
            >
              {error}
            </div>
          )}

          <div style={{ display: "flex", gap: "8px" }}>
            <input
              type="text"
              placeholder="Ask LIRIA for a recommendation..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              style={{
                flex: 1,
                padding: "8px 10px",
                borderRadius: "8px",
                border: "1px solid rgba(148,163,184,0.45)",
                backgroundColor: "rgba(15,23,42,0.9)",
                color: "#e5e7eb",
                fontSize: "14px",
                outline: "none",
                boxShadow: "0 0 0 1px rgba(15,23,42,0.9) inset",
              }}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              style={{
                padding: "8px 18px",
                borderRadius: "999px",
                border: "1px solid rgba(248,250,252,0.15)",
                cursor: isLoading || !input.trim() ? "not-allowed" : "pointer",
                background: isLoading || !input.trim()
                  ? "linear-gradient(135deg, #4b5563, #6b7280)"
                  : "linear-gradient(135deg, #f97316, #fb923c)",
                color: "#0b1120",
                fontWeight: 500,
                fontSize: "14px",
                boxShadow:
                  isLoading || !input.trim()
                    ? "none"
                    : "0 14px 30px rgba(15,23,42,0.8)",
              }}
            >
              {isLoading ? "Thinking..." : "Send"}
            </button>
          </div>
          <div
            style={{
              fontSize: "11px",
              color: "#9ca3af",
              marginTop: "4px",
            }}
          >
            Tip: talk about your favorite genres, authors, or a book you loved.
          </div>
        </section>

        {/* Side panel: quick add to library */}
        <section
          style={{
            background:
              "linear-gradient(145deg, rgba(15,23,42,0.96), rgba(15,23,42,0.9))",
            borderRadius: "20px",
            border: "1px solid rgba(148,163,184,0.25)",
            boxShadow:
              "0 22px 50px rgba(15,23,42,0.9), 0 0 0 1px rgba(15,23,42,0.8) inset",
            padding: "16px 14px",
            display: "flex",
            flexDirection: "column",
            gap: "10px",
            height: "520px",
            backdropFilter: "blur(14px)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "2px",
            }}
          >
            <div>
              <h2
                style={{
                  fontSize: "16px",
                  fontWeight: 550,
                  color: "#f9fafb",
                }}
              >
                Suggestions from LIRIA
              </h2>
              <p
                style={{
                  fontSize: "11px",
                  color: "#9ca3af",
                }}
              >
                Add recommended books directly to your library.
              </p>
            </div>
            <span style={{ fontSize: "11px", color: "#9ca3af" }}>
              {libraryCount} in library
            </span>
          </div>

          <div
            style={{
              flex: 1,
              overflowY: "auto",
              display: "flex",
              flexDirection: "column",
              gap: "6px",
              marginBottom: "6px",
            }}
          >
            {candidates.length === 0 ? (
              <div
                style={{
                  fontSize: "13px",
                  color: "#9ca3af",
                  padding: "8px 10px",
                  borderRadius: "10px",
                  border: "1px dashed rgba(148,163,184,0.5)",
                  background:
                    "linear-gradient(135deg, rgba(15,23,42,0.7), rgba(15,23,42,0.9))",
                }}
              >
                Ask LIRIA for recommendations (for example, “Give me 5 fantasy books”).
                Detected titles from the latest answer will appear here so you can add
                them in one tap.
              </div>
            ) : (
              candidates.map((title, idx) => (
                <div
                  key={idx}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: "8px",
                    padding: "6px 8px",
                    borderRadius: "10px",
                    backgroundColor: "#020617",
                    border: "1px solid rgba(148,163,184,0.5)",
                  }}
                >
                  <span
                    style={{
                      fontSize: "13px",
                      color: "#e5e7eb",
                      flex: 1,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                    title={title}
                  >
                    {title}
                  </span>
                  <button
                    onClick={() => onAddBook({ title })}
                    style={{
                      padding: "4px 10px",
                      borderRadius: "999px",
                      border: "none",
                      cursor: "pointer",
                      background:
                        "linear-gradient(135deg, #22c55e, #4ade80)",
                      color: "#022c22",
                      fontSize: "12px",
                      fontWeight: 600,
                      whiteSpace: "nowrap",
                    }}
                  >
                    + Add
                  </button>
                </div>
              ))
            )}
          </div>

          <div
            style={{
              fontSize: "11px",
              color: "#9ca3af",
            }}
          >
            Tip: LIRIA detects list items (lines starting with “-” or “•”) as book
            suggestions.
          </div>
        </section>
      </main>
    </div>
  );
}

export default ChatPage;






