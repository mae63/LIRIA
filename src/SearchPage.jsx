import React, { useMemo, useState } from "react";

// ------- Fallback client-side search (pre-LLM version) -------
// Uses Google Books (public, no key) + OpenLibrary (no key)
const GOOGLE_BOOKS_SEARCH_URL = "https://www.googleapis.com/books/v1/volumes";
const OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json";

const buildKey = (source, rawId, title) => {
  if (source && rawId) return `${source}::${rawId}`;
  return title ? title.toLowerCase() : "";
};

const normalizeGoogle = (item) => {
  const info = item.volumeInfo ?? {};
  return {
    id: `google:${item.id}`,
    source: "Google Books",
    rawId: item.id,
    title: info.title ?? "",
    authors: info.authors ?? [],
    description: info.description ?? "",
    categories: info.categories ?? [],
    coverUrl: info.imageLinks?.thumbnail || info.imageLinks?.smallThumbnail,
  };
};

const normalizeOpenLibrary = (doc) => {
  const title = doc.title ?? "";
  const authors = doc.author_name ?? [];
  const subjects = doc.subject ?? [];
  const categories = subjects.slice(0, 5);
  let description = "";
  const firstSentence = doc.first_sentence;
  if (typeof firstSentence === "string") description = firstSentence;
  if (Array.isArray(firstSentence) && firstSentence.length) description = firstSentence[0];
  if ((!description || description.length < 20) && categories.length) {
    description = "Topics: " + categories.join(", ");
  }
  if (!description) description = `${title} ${authors.slice(0, 2).join(", ")}`.trim();

  const coverUrl = doc.cover_i
    ? `https://covers.openlibrary.org/b/id/${doc.cover_i}-M.jpg`
    : undefined;

  return {
    id: `openlibrary:${doc.key ?? doc.cover_edition_key ?? title}`,
    source: "OpenLibrary",
    rawId: doc.key ?? title,
    title,
    authors,
    description,
    categories,
    coverUrl,
  };
};

const dedupe = (items) => {
  const seen = new Set();
  const out = [];
  for (const b of items) {
    const key = `${(b.title || "").toLowerCase()}|${(b.authors?.join(",") || "").toLowerCase()}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(b);
  }
  return out;
};

async function searchBooks(query, limit = 20) {
  // Google Books
  let google = [];
  try {
    const url = new URL(GOOGLE_BOOKS_SEARCH_URL);
    url.searchParams.set("q", query);
    url.searchParams.set("maxResults", Math.min(limit, 20).toString());
    const res = await fetch(url.toString());
    if (res.ok) {
      const json = await res.json();
      google = (json.items || []).map(normalizeGoogle);
    }
  } catch (_) {
    // ignore errors
  }

  // OpenLibrary
  let ol = [];
  try {
    const url = new URL(OPEN_LIBRARY_SEARCH_URL);
    url.searchParams.set("q", query);
    url.searchParams.set("limit", Math.min(limit, 20).toString());
    const res = await fetch(url.toString());
    if (res.ok) {
      const json = await res.json();
      ol = (json.docs || []).map(normalizeOpenLibrary);
    }
  } catch (_) {
    // ignore errors
  }

  const merged = dedupe([...google, ...ol]).slice(0, limit);
  if (!merged.length) throw new Error("No results found (Google+OpenLibrary).");
  return merged;
}

function SearchPage({ onAddBook, library = [] }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const addedKeys = useMemo(() => {
    const set = new Set();
    library.forEach((item) => {
      const key = buildKey(item.source, item.externalId, item.title);
      if (key) set.add(key);
    });
    return set;
  }, [library]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setResults([]);

    try {
      const data = await searchBooks(query.trim(), 20);
      setResults(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Error while searching books. Make sure the backend is running on http://localhost:8000");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAdd = (book) => {
    const key = buildKey(book.source, book.rawId, book.title);
    if (key && addedKeys.has(key)) return;

    // Handle author field (backend returns string, frontend expects array)
    const authors = book.author 
      ? [book.author] 
      : (book.authors && Array.isArray(book.authors) ? book.authors : []);

    onAddBook?.({
      title: book.title,
      rating: 0,
      comment: "",
      source: book.source,
      rawId: book.rawId,
      authors: authors,
      description: book.description,
      categories: book.categories,
      apiRating: book.apiRating,
      apiRatingsCount: book.apiRatingsCount,
      coverUrl: book.coverUrl,
    });
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
          Search books in real time
        </h1>
        <p
          style={{
            fontSize: "14px",
            lineHeight: 1.6,
            color: "#cbd5f5",
            maxWidth: "580px",
            margin: "0 auto",
          }}
        >
          Live search powered directly by Google Books and OpenLibrary (no backend). Type a title, an author, or a topic to
          see detailed results with descriptions, then add interesting books to your
          library.
        </p>
      </header>

      <main
        style={{
          maxWidth: "1080px",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          gap: "18px",
        }}
      >
        {/* Search bar */}
        <form
          onSubmit={handleSearch}
          style={{
            display: "flex",
            gap: "10px",
            alignItems: "center",
          }}
        >
          <input
            type="text"
            placeholder="Search by title, author, or topic (e.g. ‘Dune’, ‘Agatha Christie’, ‘cyberpunk’)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{
              flex: 1,
              padding: "10px 12px",
              borderRadius: "999px",
              border: "1px solid rgba(148,163,184,0.5)",
              backgroundColor: "rgba(15,23,42,0.95)",
              color: "#e5e7eb",
              fontSize: "14px",
              outline: "none",
              boxShadow: "0 0 0 1px rgba(15,23,42,0.9) inset",
            }}
          />
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            style={{
              padding: "9px 18px",
              borderRadius: "999px",
              border: "1px solid rgba(248,250,252,0.15)",
              cursor: isLoading || !query.trim() ? "not-allowed" : "pointer",
              background: isLoading || !query.trim()
                ? "linear-gradient(135deg, #4b5563, #6b7280)"
                : "linear-gradient(135deg, #22c55e, #4ade80)",
              color: "#0b1120",
              fontWeight: 500,
              fontSize: "14px",
              boxShadow:
                isLoading || !query.trim()
                  ? "none"
                  : "0 14px 30px rgba(15,23,42,0.8)",
            }}
          >
            {isLoading ? "Searching..." : "Search"}
          </button>
        </form>

        {error && (
          <div
            style={{
              fontSize: "12px",
              color: "#fecaca",
              background:
                "linear-gradient(135deg, rgba(127,29,29,0.7), rgba(127,29,29,0.4))",
              border: "1px solid rgba(248,113,113,0.8)",
              borderRadius: "6px",
              padding: "6px 10px",
            }}
          >
            {error}
          </div>
        )}

        {/* Results */}
        <section
          style={{
            background:
              "linear-gradient(145deg, rgba(15,23,42,0.96), rgba(15,23,42,0.9))",
            borderRadius: "20px",
            border: "1px solid rgba(148,163,184,0.25)",
            boxShadow:
              "0 22px 50px rgba(15,23,42,0.9), 0 0 0 1px rgba(15,23,42,0.8) inset",
            padding: "16px 16px 14px",
            display: "flex",
            flexDirection: "column",
            gap: "10px",
            maxHeight: "540px",
            overflowY: "auto",
            backdropFilter: "blur(14px)",
          }}
        >
          {results.length === 0 && !isLoading ? (
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
              No results yet. Try searching for a specific title ("Dune"), author
              ("Ursula K. Le Guin"), or theme ("space opera"). Results are pulled live from Google Books and OpenLibrary.
            </div>
          ) : (
            results.map((book) => {
              const key = buildKey(book.source, book.rawId, book.title);
              const alreadyAdded = key ? addedKeys.has(key) : false;
              return (
              <div
                key={book.id}
                style={{
                  display: "flex",
                  flexDirection: "row",
                  gap: "4px",
                  padding: "9px 10px",
                  borderRadius: "12px",
                  border: "1px solid rgba(148,163,184,0.4)",
                  backgroundColor: "#020617",
                  boxShadow: "0 10px 26px rgba(15,23,42,0.8)",
                }}
              >
                {book.coverUrl && (
                  <div
                    style={{
                      width: 58,
                      flexShrink: 0,
                      marginRight: 8,
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
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    gap: "10px",
                  }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{
                        fontSize: "14px",
                        fontWeight: 550,
                        color: "#f9fafb",
                        marginBottom: "2px",
                      }}
                    >
                      {book.title || "(Untitled book)"}
                    </div>
                    {book.author || (book.authors && book.authors.length > 0) ? (
                      <div
                        style={{
                          fontSize: "12px",
                          color: "#e5e7eb",
                          marginBottom: "2px",
                        }}
                      >
                        by {book.author || (book.authors ? book.authors.join(", ") : "Unknown Author")}
                      </div>
                    ) : null}
                    {book.description && book.description.trim().length > 0 && (
                      <div
                        style={{
                          fontSize: "12px",
                          color: "#cbd5f5",
                          marginTop: "6px",
                          lineHeight: 1.5,
                          display: "-webkit-box",
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: "vertical",
                          overflow: "hidden",
                        }}
                      >
                        {book.description.trim()}
                      </div>
                    )}
                    {book.categories?.length ? (
                      <div style={{ fontSize: "11px", color: "#9ca3af", marginTop: "4px" }}>
                        {book.categories.slice(0, 4).join(" · ")}
                      </div>
                    ) : null}
                  </div>

                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "flex-end",
                      gap: "4px",
                    }}
                  >
                    <span
                      style={{
                        fontSize: "10px",
                        padding: "2px 8px",
                        borderRadius: "999px",
                        border: "1px solid rgba(148,163,184,0.6)",
                        color: "#9ca3af",
                        textTransform: "uppercase",
                        letterSpacing: "0.08em",
                      }}
                    >
                      {book.source}
                    </span>
                    <button
                      onClick={() => handleAdd(book)}
                      disabled={alreadyAdded}
                      style={{
                        padding: "4px 10px",
                        borderRadius: "999px",
                        border: "none",
                        cursor: alreadyAdded ? "default" : "pointer",
                        background: alreadyAdded
                          ? "linear-gradient(135deg, #4b5563, #6b7280)"
                          : "linear-gradient(135deg, #22c55e, #4ade80)",
                        color: alreadyAdded ? "#cbd5f5" : "#022c22",
                        fontSize: "12px",
                        fontWeight: 600,
                        whiteSpace: "nowrap",
                      }}
                    >
                      {alreadyAdded ? "Added" : "+ Add to library"}
                    </button>
                  </div>
                </div>

                <div
                  style={{
                    fontSize: "10px",
                    color: "#6b7280",
                    marginTop: "2px",
                  }}
                >
                  ID: {book.rawId}
                </div>
              </div>
            );
          })
          )}
        </section>
      </main>
    </div>
  );
}

export default SearchPage;


