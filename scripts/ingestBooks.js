// Simple book ingestion script for LIRIA
// - Queries OpenLibrary and Google Books
// - Normalizes results into a common schema
// - Saves everything into data/books.json
//
// Run with:
//   npm run ingest
//
// You can customize the SEARCH_QUERIES array below to target genres/authors you like.

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

// ---- Config -----------------------------------------------------------------

// Example search terms; feel free to edit these
const SEARCH_QUERIES = [
  "science fiction",
  "fantasy",
  "mystery",
  "romance",
  "non-fiction",
  "classics",
];

// Limit per source per query to avoid huge files during MVP
const LIMIT_PER_QUERY_PER_SOURCE = 10;

const OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json";
const GOOGLE_BOOKS_SEARCH_URL = "https://www.googleapis.com/books/v1/volumes";

// Output file
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_DIR = path.join(__dirname, "..", "data");
const OUTPUT_FILE = path.join(DATA_DIR, "books.json");

// ---- Helpers ----------------------------------------------------------------

function ensureDataDir() {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} for ${url}`);
  }
  return res.json();
}

function normalizeOpenLibraryDoc(doc) {
  return {
    id: `openlibrary:${doc.key ?? doc.cover_edition_key ?? doc.isbn?.[0] ?? doc.title}`,
    source: "openlibrary",
    title: doc.title ?? "",
    authors: doc.author_name ?? [],
    description: "", // OpenLibrary search doesn't always give full description here
    categories: doc.subject ?? [],
    identifiers: {
      openlibrary_key: doc.key,
      isbn: doc.isbn ?? [],
    },
    publishedYear: doc.first_publish_year ?? null,
  };
}

function normalizeGoogleVolume(item) {
  const info = item.volumeInfo ?? {};
  return {
    id: `google:${item.id}`,
    source: "google_books",
    title: info.title ?? "",
    authors: info.authors ?? [],
    description: info.description ?? "",
    categories: info.categories ?? [],
    identifiers: {
      google_id: item.id,
      industryIdentifiers: info.industryIdentifiers ?? [],
    },
    publishedYear: info.publishedDate ?? null,
  };
}

// ---- Ingestion per query ----------------------------------------------------

async function ingestFromOpenLibrary(query) {
  const url = new URL(OPEN_LIBRARY_SEARCH_URL);
  url.searchParams.set("q", query);
  url.searchParams.set("limit", String(LIMIT_PER_QUERY_PER_SOURCE));

  const json = await fetchJson(url.toString());
  const docs = json.docs ?? [];
  return docs.slice(0, LIMIT_PER_QUERY_PER_SOURCE).map(normalizeOpenLibraryDoc);
}

async function ingestFromGoogleBooks(query) {
  const url = new URL(GOOGLE_BOOKS_SEARCH_URL);
  url.searchParams.set("q", query);
  url.searchParams.set("maxResults", String(LIMIT_PER_QUERY_PER_SOURCE));

  const json = await fetchJson(url.toString());
  const items = json.items ?? [];
  return items.slice(0, LIMIT_PER_QUERY_PER_SOURCE).map(normalizeGoogleVolume);
}

// ---- Main -------------------------------------------------------------------

async function main() {
  console.log("Starting book ingestion for LIRIA...");
  ensureDataDir();

  const allBooks = [];
  const seenIds = new Set();

  for (const query of SEARCH_QUERIES) {
    console.log(`\nQuery: "${query}"`);

    try {
      const [openLibBooks, googleBooks] = await Promise.all([
        ingestFromOpenLibrary(query),
        ingestFromGoogleBooks(query),
      ]);

      console.log(
        `  OpenLibrary: ${openLibBooks.length} · Google Books: ${googleBooks.length}`
      );

      for (const book of [...openLibBooks, ...googleBooks]) {
        if (!book.title) continue;
        if (seenIds.has(book.id)) continue;
        seenIds.add(book.id);
        allBooks.push(book);
      }
    } catch (err) {
      console.error(`  Error for query "${query}":`, err.message);
    }
  }

  console.log(`\nTotal unique books collected: ${allBooks.length}`);

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(allBooks, null, 2), "utf8");
  console.log(`Saved to ${OUTPUT_FILE}`);
}

main().catch((err) => {
  console.error("Fatal error during ingestion:", err);
  process.exit(1);
});








