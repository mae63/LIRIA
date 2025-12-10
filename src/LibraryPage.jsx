import React from "react";

function LibraryPage({ library, onUpdateRating }) {
  const handleRate = (book, value) => {
    if (!onUpdateRating) return;
    onUpdateRating(
      {
        ...book,
        rawId: book.externalId,
      },
      value
    );
  };

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
          My Library
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
          A simple reading log for books you have read, with ratings and short
          reflections. LIRIA uses this to understand your long‑term reading taste.
        </p>
      </header>

      <main
        style={{
          maxWidth: "1080px",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          gap: "16px",
        }}
      >
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
            gap: "10px",
            backdropFilter: "blur(14px)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-end",
              marginBottom: "4px",
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
                Saved books
              </h2>
              <p style={{ fontSize: "11px", color: "#9ca3af" }}>
                {library.length === 0
                  ? "You haven’t added any books yet."
                  : "Everything you add from chat or search appears here so you can review it later."}
              </p>
            </div>
            <span style={{ fontSize: "11px", color: "#9ca3af" }}>
              {library.length} total
            </span>
          </div>

          <div
            style={{
              maxHeight: "460px",
              overflowY: "auto",
              display: "flex",
              flexDirection: "column",
              gap: "8px",
            }}
          >
            {library.length === 0 ? (
              <div
                style={{
                  fontSize: "13px",
                  color: "#9ca3af",
                  padding: "10px 12px",
                  borderRadius: "10px",
                  border: "1px dashed rgba(148,163,184,0.5)",
                  background:
                    "linear-gradient(135deg, rgba(15,23,42,0.7), rgba(15,23,42,0.9))",
                }}
              >
                No entries yet. You can add books directly from the chat page, or
                manually here by deciding on a title, a rating, and a short comment.
              </div>
            ) : (
              library.map((book, index) => (
                <div
                  key={`${book.title}-${index}`}
                  style={{
                    textAlign: "left",
                    border: "1px solid rgba(148,163,184,0.35)",
                    borderRadius: "12px",
                    padding: "9px 10px",
                    fontSize: "13px",
                    background:
                      "radial-gradient(circle at top, rgba(30,64,175,0.5), rgba(15,23,42,0.98))",
                    boxShadow: "0 10px 26px rgba(15,23,42,0.8)",
                    display: "flex",
                    flexDirection: "row",
                    gap: "8px",
                  }}
                >
                  {book.coverUrl && (
                    <div
                      style={{
                        width: 58,
                        flexShrink: 0,
                      }}
                    >
                      <img
                        src={book.coverUrl}
                        alt={book.title}
                        style={{
                          width: "100%",
                          height: "auto",
                          borderRadius: 6,
                          objectFit: "cover",
                          backgroundColor: "#020617",
                        }}
                      />
                    </div>
                  )}
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "3px",
                    }}
                  >
                    <span
                      style={{
                        fontWeight: 550,
                        color: "#f9fafb",
                      }}
                    >
                      {book.title}
                    </span>
                    {book.authors?.length ? (
                      <span
                        style={{
                          fontSize: "12px",
                          color: "#e5e7eb",
                        }}
                      >
                        by {book.authors.join(", ")}
                      </span>
                    ) : null}
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "4px",
                      }}
                    >
                      <span
                        style={{
                          fontSize: "12px",
                          color: "#e5e7eb",
                        }}
                      >
                        {book.rating > 0
                          ? `Your rating: ${book.rating}/5`
                          : "Rate this book:"}
                      </span>
                      <div
                        style={{
                          display: "flex",
                          gap: "4px",
                        }}
                      >
                        {[1, 2, 3, 4, 5].map((value) => {
                          const active = value <= (book.rating || 0);
                          return (
                            <button
                              key={value}
                              type="button"
                              onClick={() => handleRate(book, value)}
                              style={{
                                border: "none",
                                background: "transparent",
                                color: active ? "#fde68a" : "#475569",
                                fontSize: "18px",
                                cursor: "pointer",
                                padding: 0,
                              }}
                              aria-label={`Rate ${value} star${value > 1 ? "s" : ""}`}
                            >
                              {active ? "★" : "☆"}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                    {typeof book.apiRating === "number" && (
                      <span
                        style={{
                          fontSize: "11px",
                          color: "#fbbf24",
                        }}
                      >
                        Community: {book.apiRating.toFixed(1)}/5{" "}
                        {book.apiRatingsCount
                          ? `(${book.apiRatingsCount} ratings)`
                          : ""}
                      </span>
                    )}
                    {book.categories?.length ? (
                      <span
                        style={{
                          fontSize: "11px",
                          color: "#9ca3af",
                        }}
                      >
                        {book.categories.slice(0, 4).join(" · ")}
                      </span>
                    ) : null}
                    {book.comment && (
                      <span style={{ fontSize: "12px", color: "#9ca3af" }}>
                        “{book.comment}”
                      </span>
                    )}
                    {(book.source || book.externalId) && (
                      <span
                        style={{
                          fontSize: "10px",
                          color: "#6b7280",
                          marginTop: "2px",
                        }}
                      >
                        {book.source ? `${book.source} ` : ""}
                        {book.externalId ? `ID: ${book.externalId}` : ""}
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default LibraryPage;


