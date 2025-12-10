import React, { useEffect, useRef, useState } from "react";

function LiriaApp() {
  // Conversation
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hi, I'm LIRIA. Tell me what kind of book you're looking for.",
    },
  ]);
  const [input, setInput] = useState("");

  // Library: { title, rating, comment }
  const [library, setLibrary] = useState([]);
  const [newTitle, setNewTitle] = useState("");
  const [newRating, setNewRating] = useState(3);
  const [newComment, setNewComment] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const chatRef = useRef(null);

  // TODO: remplace cette URL par celle de ton backend (Replit ou autre)
  const BACKEND_URL = "http://localhost:8000/chat";

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: "user", content: input.trim() };
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

      const aiMessage = { role: "assistant", content: replyText };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error(err);
      setError("There was an error communicating with the server.");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I had a server issue. Please try again later.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const addToLibrary = () => {
    const title = newTitle.trim();
    if (!title) return;

    setLibrary((prev) => {
      const existingIndex = prev.findIndex(
        (b) => b.title.toLowerCase() === title.toLowerCase()
      );

      const bookData = {
        title,
        rating: Number(newRating) || 0,
        comment: newComment.trim(),
      };

      if (existingIndex !== -1) {
        const copy = [...prev];
        copy[existingIndex] = bookData;
        return copy;
      }
      return [...prev, bookData];
    });

    // reset form
    setNewTitle("");
    setNewRating(3);
    setNewComment("");
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

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top, #1d4ed8 0, transparent 55%), radial-gradient(circle at bottom, #7c3aed 0, #020617 55%)",
        color: "#e5e7eb",
        padding: "32px 16px 32px",
        display: "flex",
        flexDirection: "column",
        gap: "24px",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      {/* HEADER */}
      <header
        style={{
          maxWidth: "1080px",
          margin: "0 auto",
          textAlign: "center",
        }}
      >
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            padding: "4px 10px",
            borderRadius: "999px",
            backgroundColor: "rgba(15,23,42,0.7)",
            border: "1px solid rgba(148,163,184,0.4)",
            marginBottom: "10px",
          }}
        >
          <span
            style={{
              width: "6px",
              height: "6px",
              borderRadius: "999px",
              background:
                "radial-gradient(circle at center, #22c55e 0, #16a34a 45%, transparent 60%)",
              boxShadow: "0 0 12px rgba(34,197,94,0.7)",
            }}
          />
          <span
            style={{
              fontSize: "10px",
              textTransform: "uppercase",
              letterSpacing: "0.3em",
              color: "#9ca3af",
            }}
          >
            AI Literary Companion
          </span>
        </div>
        <h1
          style={{
            fontSize: "30px",
            fontWeight: 650,
            marginBottom: "6px",
            letterSpacing: "-0.04em",
            color: "#f9fafb",
            textShadow: "0 18px 45px rgba(15,23,42,0.9)",
          }}
        >
          LIRIA — AI Literary Advisor
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
          suggest titles and help you build your library.
        </p>
      </header>

      {/* MAIN */}
      <main
        style={{
          maxWidth: "1080px",
          margin: "0 auto",
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: "18px",
          alignItems: "stretch",
        }}
      >
        {/* CHAT */}
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
            height: "500px",
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
            {messages.map((msg, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                  gap: "8px",
                }}
              >
                {msg.role === "assistant" && (
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
                    borderRadius: msg.role === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
                    fontSize: "14px",
                    backgroundColor:
                      msg.role === "user"
                        ? "linear-gradient(135deg, #e5e7eb, #f9fafb)"
                        : "linear-gradient(135deg, rgba(30,64,175,0.25), rgba(15,23,42,0.95))",
                    color: msg.role === "user" ? "#020617" : "#e5e7eb",
                    border: msg.role === "user"
                      ? "1px solid rgba(148,163,184,0.45)"
                      : "1px solid rgba(129,140,248,0.45)",
                    boxShadow:
                      msg.role === "user"
                        ? "0 10px 25px rgba(15,23,42,0.55)"
                        : "0 10px 25px rgba(15,23,42,0.65)",
                    lineHeight: 1.5,
                    whiteSpace: "pre-wrap",
                    transition: "transform 120ms ease-out, box-shadow 120ms ease-out",
                  }}
                >
                  {msg.content}
                </div>
              </div>
            ))}
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
                boxShadow: isLoading || !input.trim()
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

        {/* LIBRARY */}
        <section
          style={{
            background:
              "linear-gradient(145deg, rgba(15,23,42,0.96), rgba(15,23,42,0.9))",
            borderRadius: "20px",
            border: "1px solid rgba(148,163,184,0.25)",
            boxShadow:
              "0 22px 50px rgba(15,23,42,0.9), 0 0 0 1px rgba(15,23,42,0.8) inset",
            padding: "18px 16px 14px",
            display: "flex",
            flexDirection: "column",
            height: "500px",
            backdropFilter: "blur(14px)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "8px",
            }}
          >
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-start",
                gap: "2px",
              }}
            >
              <h2 style={{ fontSize: "17px", fontWeight: 550, color: "#f9fafb" }}>
                My Library
              </h2>
              <span style={{ fontSize: "11px", color: "#9ca3af" }}>
                Books you’ve read and rated
              </span>
            </div>
            <span style={{ fontSize: "11px", color: "#9ca3af" }}>
              {library.length} saved
            </span>
          </div>

          {/* List of saved books */}
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              display: "flex",
              flexDirection: "column",
              gap: "7px",
              marginBottom: "8px",
            }}
          >
            {library.length === 0 ? (
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
                No entries yet. Add books you’ve read with a rating and a short comment
                to build your long‑term reading profile.
              </div>
            ) : (
              library.map((book, i) => (
                <div
                  key={i}
                  style={{
                    border: "1px solid rgba(148,163,184,0.35)",
                    borderRadius: "12px",
                    padding: "7px 9px",
                    fontSize: "13px",
                    background:
                      "radial-gradient(circle at top, rgba(30,64,175,0.5), rgba(15,23,42,0.98))",
                    boxShadow: "0 10px 26px rgba(15,23,42,0.8)",
                    display: "flex",
                    flexDirection: "column",
                    gap: "2px",
                  }}
                >
                  <span style={{ fontWeight: 550 }}>{book.title}</span>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      gap: "4px",
                    }}
                  >
                    <span style={{ fontSize: "12px", color: "#e5e7eb" }}>
                      Rating:{" "}
                      <span style={{ color: "#fde68a" }}>
                        {book.rating}/5{" "}
                        {"★".repeat(book.rating || 0)}
                      </span>
                    </span>
                  </div>
                  {book.comment && (
                    <span style={{ fontSize: "12px", color: "#9ca3af" }}>
                      “{book.comment}”
                    </span>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Add book form */}
          <div
            style={{
              borderTop: "1px solid #1f2937",
              paddingTop: "8px",
              display: "flex",
              flexDirection: "column",
              gap: "6px",
            }}
          >
            <div style={{ fontSize: "12px", color: "#9ca3af" }}>
              Add a book you’ve read (used to build your long‑term reading profile).
            </div>
            <input
              type="text"
              placeholder="Book title"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              style={{
                padding: "6px 8px",
                borderRadius: "6px",
                border: "1px solid rgba(148,163,184,0.45)",
                backgroundColor: "rgba(15,23,42,0.9)",
                color: "#e5e7eb",
                fontSize: "13px",
              }}
            />
            <div
              style={{
                display: "flex",
                gap: "8px",
                alignItems: "center",
              }}
            >
              <label style={{ fontSize: "12px", color: "#9ca3af" }}>
                Rating (1 to 5)
              </label>
              <input
                type="number"
                min="1"
                max="5"
                value={newRating}
                onChange={(e) => setNewRating(e.target.value)}
                style={{
                  width: "60px",
                  padding: "4px 6px",
                  borderRadius: "6px",
                  border: "1px solid rgba(148,163,184,0.45)",
                  backgroundColor: "rgba(15,23,42,0.9)",
                  color: "#e5e7eb",
                  fontSize: "13px",
                }}
              />
            </div>
            <textarea
              placeholder="Short comment (optional)"
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              rows={2}
              style={{
                padding: "6px 8px",
                borderRadius: "6px",
                border: "1px solid rgba(148,163,184,0.45)",
                backgroundColor: "rgba(15,23,42,0.9)",
                color: "#e5e7eb",
                fontSize: "13px",
                resize: "vertical",
              }}
            />
            <button
              onClick={addToLibrary}
              disabled={!newTitle.trim()}
              style={{
                marginTop: "2px",
                padding: "6px 10px",
                borderRadius: "8px",
                border: "none",
                cursor: !newTitle.trim() ? "not-allowed" : "pointer",
                backgroundColor: !newTitle.trim() ? "#4b5563" : "#e5e7eb",
                color: "#020617",
                fontWeight: 500,
                fontSize: "13px",
                alignSelf: "flex-end",
              }}
            >
              Save to my library
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

export default LiriaApp;


