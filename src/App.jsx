import React, { useEffect, useMemo, useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import ChatPage from "./ChatPage.jsx";
import LibraryPage from "./LibraryPage.jsx";
import SearchPage from "./SearchPage.jsx";
import LiriaLogo from "./components/LiriaLogo.jsx";

const LOCAL_STORAGE_KEY = "liria-library";
const buildKey = (source, rawId, title) => {
  if (source && rawId) return `${source}::${rawId}`;
  return title ? title.toLowerCase() : "";
};

function App() {
  const [library, setLibrary] = useState([]);

  // Load library from localStorage on first mount
  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(LOCAL_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          setLibrary(parsed);
        }
      }
    } catch (err) {
      console.error("Failed to load library from localStorage", err);
    }
  }, []);

  // Persist library whenever it changes
  useEffect(() => {
    try {
      window.localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(library));
    } catch (err) {
      console.error("Failed to save library to localStorage", err);
    }
  }, [library]);

  const handleAddBook = (book) => {
    // book: { title, rating?, comment?, source?, rawId?, authors?, description?, categories?, apiRating?, apiRatingsCount?, coverUrl? }
    if (!book?.title?.trim()) return;
    const title = book.title.trim();

    setLibrary((prev) => {
      const key = buildKey(book.source, book.rawId, title);
      const existingIndex = prev.findIndex((b) => {
        const existingKey = buildKey(b.source, b.externalId, b.title);
        return existingKey === key;
      });

      const rating = typeof book.rating === "number" ? book.rating : 0;
      const comment = book.comment?.trim() || "";
      const source = book.source || null;
      const externalId = book.rawId || null;
      const authors = Array.isArray(book.authors) ? book.authors : [];
      const description = book.description || "";
      const categories = Array.isArray(book.categories) ? book.categories : [];
      const apiRating =
        typeof book.apiRating === "number" ? book.apiRating : null;
      const apiRatingsCount =
        typeof book.apiRatingsCount === "number" ? book.apiRatingsCount : null;
      const coverUrl = book.coverUrl || null;

      const payload = {
        title,
        rating,
        comment,
        source,
        externalId,
        authors,
        description,
        categories,
        apiRating,
        apiRatingsCount,
        coverUrl,
      };

      if (existingIndex !== -1) {
        const copy = [...prev];
        copy[existingIndex] = payload;
        return copy;
      }

      return [...prev, payload];
    });
  };

  const handleUpdateRating = (bookInfo, newRating) => {
    setLibrary((prev) =>
      prev.map((item) => {
        const currentKey = buildKey(item.source, item.externalId, item.title);
        const targetKey = buildKey(bookInfo.source, bookInfo.rawId, bookInfo.title);
        if (currentKey === targetKey) {
          return { ...item, rating: newRating };
        }
        return item;
      })
    );
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top, #1d4ed8 0, transparent 55%), radial-gradient(circle at bottom, #7c3aed 0, #020617 55%)",
        color: "#e5e7eb",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      {/* Navbar */}
      <nav
        style={{
          position: "sticky",
          top: 0,
          zIndex: 20,
          backdropFilter: "blur(14px)",
          backgroundColor: "rgba(2,6,23,0.92)",
          borderBottom: "1px solid rgba(15,23,42,0.9)",
        }}
      >
        <div
          style={{
            maxWidth: "1080px",
            margin: "0 auto",
            padding: "10px 16px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "16px",
          }}
        >
          <LiriaLogo size={46} showWordmark />

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              fontSize: 13,
            }}
          >
            <NavLink
              to="/"
              style={({ isActive }) => ({
                padding: "6px 10px",
                borderRadius: 999,
                textDecoration: "none",
                color: isActive ? "#0b1120" : "#e5e7eb",
                backgroundColor: isActive ? "#e5e7eb" : "transparent",
                border: isActive ? "1px solid rgba(148,163,184,0.7)" : "none",
              })}
              end
            >
              Chat
            </NavLink>
            <NavLink
              to="/search"
              style={({ isActive }) => ({
                padding: "6px 10px",
                borderRadius: 999,
                textDecoration: "none",
                color: isActive ? "#0b1120" : "#e5e7eb",
                backgroundColor: isActive ? "#e5e7eb" : "transparent",
                border: isActive ? "1px solid rgba(148,163,184,0.7)" : "none",
              })}
            >
              Search
            </NavLink>
            <NavLink
              to="/library"
              style={({ isActive }) => ({
                padding: "6px 10px",
                borderRadius: 999,
                textDecoration: "none",
                color: isActive ? "#0b1120" : "#e5e7eb",
                backgroundColor: isActive ? "#e5e7eb" : "transparent",
                border: isActive ? "1px solid rgba(148,163,184,0.7)" : "none",
              })}
            >
              My Library
            </NavLink>
          </div>
        </div>
      </nav>

      {/* Route content */}
      <Routes>
        <Route
          path="/"
          element={
            <ChatPage
              onAddBook={handleAddBook}
              libraryCount={library.length}
            />
          }
        />
        <Route
          path="/library"
          element={
            <LibraryPage
              library={library}
              onUpdateRating={handleUpdateRating}
            />
          }
        />
        <Route
          path="/search"
          element={<SearchPage onAddBook={handleAddBook} library={library} />}
        />
        {/* Fallback: redirect unknown paths to chat */}
        <Route
          path="*"
          element={
            <ChatPage
              onAddBook={handleAddBook}
              libraryCount={library.length}
            />
          }
        />
      </Routes>
    </div>
  );
}

export default App;


