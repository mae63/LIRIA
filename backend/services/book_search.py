"""
Book Search Service
Fetches and normalizes book data from Google Books and OpenLibrary APIs.
"""

import asyncio
import os
from typing import List, Dict
import httpx
from models.book import Book


GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"


async def fetch_google_books(query: str, max_results: int = 20, api_key: str | None = None) -> List[Dict]:
    """Fetch books from Google Books API (optionally with API key for higher quota)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {
                "q": query,
                "maxResults": min(max_results, 40),  # Google API limit
                "fields": "items(id,volumeInfo(title,authors,description,categories,imageLinks,industryIdentifiers,publisher,publishedDate,previewLink))"
            }
            if api_key:
                params["key"] = api_key
            response = await client.get(GOOGLE_BOOKS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
    except httpx.TimeoutException:
        return []
    except httpx.HTTPStatusError:
        return []
    except Exception:
        return []


async def fetch_openlibrary_books(query: str, limit: int = 20) -> List[Dict]:
    """Fetch books from OpenLibrary API"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            params = {
                "q": query,
                "limit": min(limit, 100),  # OpenLibrary limit
            }
            response = await client.get(OPEN_LIBRARY_SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("docs", [])
    except httpx.TimeoutException:
        return []
    except httpx.HTTPStatusError:
        return []
    except Exception:
        return []


def normalize_google_book(item: Dict) -> Book:
    """Normalize a Google Books API result"""
    volume_info = item.get("volumeInfo", {})
    
    title = volume_info.get("title", "").strip()
    authors = volume_info.get("authors", [])
    author = ", ".join(authors) if authors else "Unknown Author"
    
    description = volume_info.get("description", "").strip()
    # Keep full description - don't truncate (LLM needs complete info)
    
    categories = volume_info.get("categories", [])
    if isinstance(categories, str):
        categories = [categories]
    categories = [cat.strip() for cat in categories if cat]
    
    image_links = volume_info.get("imageLinks", {})
    thumbnail = (
        image_links.get("thumbnail") or
        image_links.get("smallThumbnail") or
        None
    )
    
    # Extract ISBN (prefer ISBN_13, fallback to ISBN_10)
    isbn = None
    industry_identifiers = volume_info.get("industryIdentifiers", [])
    for identifier in industry_identifiers:
        if identifier.get("type") == "ISBN_13":
            isbn = identifier.get("identifier", "").strip()
            break
        elif identifier.get("type") == "ISBN_10" and not isbn:
            isbn = identifier.get("identifier", "").strip()
    
    publisher = volume_info.get("publisher", "").strip() or None
    published_date = volume_info.get("publishedDate", "").strip() or None
    preview_link = volume_info.get("previewLink", "").strip() or None
    
    return Book(
        id=f"google:{item.get('id', '')}",
        title=title,
        author=author,
        description=description,
        categories=categories,
        thumbnail=thumbnail,
        source="Google Books",
        isbn=isbn,
        publisher=publisher,
        published_date=published_date,
        preview_link=preview_link
    )


def normalize_openlibrary_book(doc: Dict) -> Book:
    """Normalize an OpenLibrary API result"""
    title = doc.get("title", "").strip()
    
    author_names = doc.get("author_name", [])
    author = ", ".join(author_names[:3]) if author_names else "Unknown Author"
    
    # OpenLibrary rarely returns descriptions; fallback to first_sentence or subjects
    first_sentence = doc.get("first_sentence", [])
    if isinstance(first_sentence, list) and first_sentence:
        description = " ".join(first_sentence[:2])
    elif isinstance(first_sentence, str):
        description = first_sentence
    else:
        description = ""
    
    subjects = doc.get("subject", [])
    categories = [s.strip() for s in subjects[:5] if isinstance(s, str)]
    # If no usable description, build a short topical blurb from subjects
    if (not description or len(description.strip()) < 20) and categories:
        description = "Topics: " + ", ".join(categories[:6])
    # As a last resort, synthesize a tiny blurb to avoid dropping the book
    if not description or len(description.strip()) < 5:
        description = f"{title} by {author}"
    
    # Build cover URL if cover_i is available
    cover_i = doc.get("cover_i")
    thumbnail = None
    if cover_i:
        thumbnail = f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg"
    
    # Use key or isbn as ID
    book_id = doc.get("key", "").replace("/works/", "").replace("/books/", "")
    if not book_id and doc.get("isbn"):
        isbn_list = doc.get("isbn", [])
        book_id = isbn_list[0] if isbn_list else ""
    
    return Book(
        id=f"openlibrary:{book_id}",
        title=title,
        author=author,
        description=description,
        categories=categories,
        thumbnail=thumbnail,
        source="OpenLibrary"
    )


def filter_books(books: List[Book]) -> List[Book]:
    """Filter out books without meaningful title or description, and prioritize individual novels over collections"""
    filtered = []
    
    # Keywords that indicate collections/anthologies (lowercase for case-insensitive matching)
    collection_keywords = [
        "megapack", "collection", "anthology", "box set", "boxset",
        "best of", "best-of", "compilation", "omnibus", "complete",
        "series collection", "boxed set", "boxed collection"
    ]
    
    for book in books:
        # Must have a title
        if not book.title or len(book.title.strip()) < 2:
            continue
        
        # Skip collections/anthologies (but keep them if they're the only results)
        title_lower = book.title.lower()
        is_collection = any(keyword in title_lower for keyword in collection_keywords)
        
        # Keep if description is at least 10 chars OR we have some categories/topics
        has_description = book.description and len(book.description.strip()) >= 10
        has_topics = bool(book.categories)
        if not (has_description or has_topics):
            continue
        
        # For now, keep all books (we'll prioritize individual novels in the LLM prompt)
        # But mark collections for lower priority
        filtered.append(book)
    
    # Sort: individual novels first, then collections
    def sort_key(book):
        title_lower = book.title.lower()
        is_collection = any(keyword in title_lower for keyword in collection_keywords)
        return (1 if is_collection else 0)  # 0 = individual novel (first), 1 = collection (last)
    
    filtered.sort(key=sort_key)
    return filtered


def deduplicate_books(books: List[Book]) -> List[Book]:
    """Deduplicate books based on title + author combination"""
    seen = set()
    unique_books = []
    
    for book in books:
        # Create a key from normalized title + author
        key = f"{book.title.lower().strip()}|{book.author.lower().strip()}"
        
        if key not in seen:
            seen.add(key)
            unique_books.append(book)
    
    return unique_books


def filter_books_strict(books: List[Book], min_fields: int = 3, max_results: int = 8) -> List[Book]:
    """
    Strictly filter books by keeping only those with at least min_fields (default 3) 
    of the following fields present and non-empty: ISBN, publisher, categories, publishedDate, previewLink.
    Returns the best-structured books (up to max_results).
    """
    required_fields = ["isbn", "publisher", "categories", "published_date", "preview_link"]
    
    filtered = []
    for book in books:
        field_count = 0
        
        # Check ISBN
        if book.isbn and book.isbn.strip():
            field_count += 1
        
        # Check publisher
        if book.publisher and book.publisher.strip():
            field_count += 1
        
        # Check categories (must have at least one)
        if book.categories and len(book.categories) > 0:
            field_count += 1
        
        # Check published_date
        if book.published_date and book.published_date.strip():
            field_count += 1
        
        # Check preview_link
        if book.preview_link and book.preview_link.strip():
            field_count += 1
        
        # Keep only books with at least min_fields
        if field_count >= min_fields:
            filtered.append((book, field_count))
    
    # Sort by number of fields (best-structured first), then by description length
    filtered.sort(key=lambda x: (x[1], len(x[0].description or "")), reverse=True)
    
    # Return top max_results books
    return [book for book, _ in filtered[:max_results]]


async def search_books_from_apis(query: str, limit: int = 20) -> List[Book]:
    """
    Main function to search books from both APIs, normalize, filter, and deduplicate.
    """
    if not query or not query.strip():
        return []
    
    google_api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
    use_google = os.getenv("USE_GOOGLE_BOOKS", "true").lower() in {"1", "true", "yes"}

    tasks = []
    if use_google:
        tasks.append(fetch_google_books(query, limit, api_key=google_api_key))
    tasks.append(fetch_openlibrary_books(query, limit))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    google_items = []
    openlibrary_docs = []

    # Unpack results based on whether Google was used
    if use_google:
        if len(results) >= 1 and not isinstance(results[0], Exception):
            google_items = results[0] or []
        if len(results) >= 2 and not isinstance(results[1], Exception):
            openlibrary_docs = results[1] or []
    else:
        if len(results) >= 1 and not isinstance(results[0], Exception):
            openlibrary_docs = results[0] or []

    # Normalize all books
    normalized_books = []

    for item in google_items:
        try:
            book = normalize_google_book(item)
            normalized_books.append(book)
        except Exception:
            continue

    for doc in openlibrary_docs:
        try:
            book = normalize_openlibrary_book(doc)
            normalized_books.append(book)
        except Exception:
            continue

    # Filter out books without descriptions/titles
    filtered_books = filter_books(normalized_books)

    # Deduplicate
    unique_books = deduplicate_books(filtered_books)

    return unique_books[:limit]

