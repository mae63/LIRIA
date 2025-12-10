"""
LIRIA - AI Literary Advisor
Streamlit application for book recommendations, search, and personal library management.
"""

import streamlit as st
import requests
import json
from typing import List, Dict, Optional
import os

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
STREAMLIT_CLOUD = os.getenv("STREAMLIT_CLOUD", "false").lower() == "true"

# If running on Streamlit Cloud, use the backend URL from environment
if STREAMLIT_CLOUD:
    BACKEND_URL = os.getenv("BACKEND_URL", "https://your-backend-url.herokuapp.com")

# Page configuration
st.set_page_config(
    page_title="LIRIA - AI Literary Advisor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .book-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        background: #fafafa;
    }
    .chat-message {
        padding: 0.75rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    .assistant-message {
        background: #f0f0f0;
        margin-right: 20%;
    }
    .star-rating {
        font-size: 1.5rem;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "library" not in st.session_state:
    st.session_state.library = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hi, I'm LIRIA. Tell me what kind of book you're looking for."}
    ]
if "search_results" not in st.session_state:
    st.session_state.search_results = []


def load_library():
    """Load library from session state"""
    return st.session_state.library


def save_library(library):
    """Save library to session state"""
    st.session_state.library = library


def add_book_to_library(book: Dict):
    """Add a book to the library"""
    library = load_library()
    # Check if book already exists
    existing = next(
        (b for b in library if b.get("title") == book.get("title") and 
         b.get("authors") == book.get("authors")), None
    )
    if not existing:
        book_entry = {
            "title": book.get("title", ""),
            "authors": book.get("authors", []),
            "description": book.get("description", ""),
            "categories": book.get("categories", []),
            "source": book.get("source", ""),
            "rawId": book.get("rawId", ""),
            "coverUrl": book.get("coverUrl", ""),
            "rating": 0,
            "comment": "",
            "apiRating": book.get("apiRating"),
            "apiRatingsCount": book.get("apiRatingsCount"),
        }
        library.append(book_entry)
        save_library(library)
        return True
    return False


def update_book_rating(book_index: int, rating: int):
    """Update rating for a book in the library"""
    library = load_library()
    if 0 <= book_index < len(library):
        library[book_index]["rating"] = rating
        save_library(library)


def send_chat_message(message: str) -> Optional[Dict]:
    """Send a message to the chat backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": message, "limit": 6},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to backend: {str(e)}")
        return None


def search_books_backend(query: str, limit: int = 20) -> List[Dict]:
    """Search books using the backend API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/search",
            json={"query": query, "limit": limit},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to backend: {str(e)}")
        return []


def search_books_direct(query: str, limit: int = 20) -> List[Dict]:
    """Direct search using Google Books and OpenLibrary (fallback)"""
    results = []
    
    # Google Books
    try:
        google_url = "https://www.googleapis.com/books/v1/volumes"
        params = {"q": query, "maxResults": min(limit, 20)}
        response = requests.get(google_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("items", []):
                info = item.get("volumeInfo", {})
                results.append({
                    "id": f"google:{item.get('id')}",
                    "title": info.get("title", ""),
                    "authors": info.get("authors", []),
                    "description": info.get("description", ""),
                    "categories": info.get("categories", []),
                    "coverUrl": info.get("imageLinks", {}).get("thumbnail", ""),
                    "source": "Google Books",
                    "rawId": item.get("id", ""),
                    "apiRating": info.get("averageRating"),
                    "apiRatingsCount": info.get("ratingsCount"),
                })
    except Exception as e:
        st.warning(f"Google Books search failed: {str(e)}")
    
    # OpenLibrary
    try:
        ol_url = "https://openlibrary.org/search.json"
        params = {"q": query, "limit": min(limit, 20)}
        response = requests.get(ol_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for doc in data.get("docs", []):
                cover_id = doc.get("cover_i")
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else ""
                results.append({
                    "id": f"openlibrary:{doc.get('key', '')}",
                    "title": doc.get("title", ""),
                    "authors": doc.get("author_name", []),
                    "description": doc.get("first_sentence", [""])[0] if doc.get("first_sentence") else "",
                    "categories": doc.get("subject", [])[:5],
                    "coverUrl": cover_url,
                    "source": "OpenLibrary",
                    "rawId": doc.get("key", ""),
                })
    except Exception as e:
        st.warning(f"OpenLibrary search failed: {str(e)}")
    
    # Deduplicate
    seen = set()
    unique_results = []
    for book in results:
        key = f"{book.get('title', '').lower()}|{','.join(book.get('authors', [])).lower()}"
        if key not in seen:
            seen.add(key)
            unique_results.append(book)
    
    return unique_results[:limit]


# Sidebar navigation
st.sidebar.title("📚 LIRIA")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["💬 Chat", "🔍 Search", "📖 My Library"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Library:** {len(st.session_state.library)} books")

# Main content based on selected page
if page == "💬 Chat":
    st.markdown('<h1 class="main-header">LIRIA — Chat</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align: center; color: #666; margin-bottom: 2rem;">
        Describe your mood, your favorite authors, or a recent book. 
        LIRIA will suggest titles and help you build your long‑term reading profile.
    </p>
    """, unsafe_allow_html=True)
    
    # Chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message">{msg["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Ask LIRIA for a recommendation...",
            key="chat_input",
            label_visibility="collapsed"
        )
    with col2:
        send_button = st.button("Send", type="primary", use_container_width=True)
    
    if send_button and user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get AI response
        with st.spinner("LIRIA is thinking..."):
            response = send_chat_message(user_input)
        
        if response:
            reply = response.get("reply", "I couldn't generate a response.")
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            
            # Show recommended books from response
            books = response.get("books", [])
            if books:
                st.markdown("### 📚 Recommended Books")
                for book in books:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"**{book.get('title', 'Unknown')}** by {book.get('author', 'Unknown')}")
                        if book.get('description'):
                            st.caption(book.get('description')[:200] + "...")
                    with col2:
                        if st.button("Add", key=f"add_{book.get('id')}"):
                            book_dict = {
                                "title": book.get("title", ""),
                                "authors": [book.get("author", "")],
                                "description": book.get("description", ""),
                                "categories": book.get("categories", []),
                                "source": book.get("source", ""),
                                "rawId": book.get("id", ""),
                                "coverUrl": book.get("thumbnail", ""),
                            }
                            if add_book_to_library(book_dict):
                                st.success("Added to library!")
                                st.rerun()
        
        st.rerun()

elif page == "🔍 Search":
    st.markdown('<h1 class="main-header">Search Books</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align: center; color: #666; margin-bottom: 2rem;">
        Live search powered by Google Books and OpenLibrary. 
        Type a title, an author, or a topic to see detailed results.
    </p>
    """, unsafe_allow_html=True)
    
    # Search input
    col1, col2 = st.columns([5, 1])
    with col1:
        search_query = st.text_input(
            "Search by title, author, or topic...",
            key="search_input",
            label_visibility="collapsed"
        )
    with col2:
        search_button = st.button("Search", type="primary", use_container_width=True)
    
    use_backend = st.checkbox("Use backend API (if available)", value=False)
    
    if search_button and search_query:
        with st.spinner("Searching..."):
            if use_backend:
                results = search_books_backend(search_query, 20)
            else:
                results = search_books_direct(search_query, 20)
            st.session_state.search_results = results
    
    # Display results
    if st.session_state.search_results:
        st.markdown(f"### Found {len(st.session_state.search_results)} results")
        for book in st.session_state.search_results:
            with st.container():
                col1, col2, col3 = st.columns([1, 4, 1])
                
                with col1:
                    if book.get("coverUrl"):
                        st.image(book.get("coverUrl"), width=100)
                    else:
                        st.write("📚")
                
                with col2:
                    st.write(f"**{book.get('title', 'Unknown')}**")
                    authors = book.get("authors", [])
                    if authors:
                        st.write(f"by {', '.join(authors) if isinstance(authors, list) else authors}")
                    if book.get("description"):
                        st.caption(book.get("description")[:300] + "...")
                    if book.get("categories"):
                        categories = book.get("categories", [])
                        if isinstance(categories, list):
                            st.write(f"Tags: {', '.join(categories[:4])}")
                    st.caption(f"Source: {book.get('source', 'Unknown')}")
                
                with col3:
                    library = load_library()
                    is_added = any(
                        b.get("title") == book.get("title") and 
                        b.get("authors") == (book.get("authors") if isinstance(book.get("authors"), list) else [book.get("authors")])
                        for b in library
                    )
                    if not is_added:
                        if st.button("Add", key=f"search_add_{book.get('id')}"):
                            if add_book_to_library(book):
                                st.success("Added!")
                                st.rerun()
                    else:
                        st.info("Added ✓")
                
                st.divider()

elif page == "📖 My Library":
    st.markdown('<h1 class="main-header">My Library</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align: center; color: #666; margin-bottom: 2rem;">
        A simple reading log for books you have read, with ratings and short reflections.
    </p>
    """, unsafe_allow_html=True)
    
    library = load_library()
    
    if not library:
        st.info("Your library is empty. Add books from Chat or Search!")
    else:
        for idx, book in enumerate(library):
            with st.container():
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    if book.get("coverUrl"):
                        st.image(book.get("coverUrl"), width=100)
                    else:
                        st.write("📚")
                
                with col2:
                    st.write(f"**{book.get('title', 'Unknown')}**")
                    if book.get("authors"):
                        authors = book.get("authors", [])
                        if isinstance(authors, list):
                            st.write(f"by {', '.join(authors)}")
                        else:
                            st.write(f"by {authors}")
                    
                    # Rating
                    st.write("Your rating:")
                    rating_cols = st.columns(5)
                    current_rating = book.get("rating", 0)
                    for i, col in enumerate(rating_cols):
                        with col:
                            star_value = i + 1
                            if st.button("★" if star_value <= current_rating else "☆", key=f"rate_{idx}_{star_value}"):
                                update_book_rating(idx, star_value)
                                st.rerun()
                    
                    if book.get("apiRating"):
                        st.caption(f"Community: {book.get('apiRating')}/5 ({book.get('apiRatingsCount', 0)} ratings)")
                    
                    if book.get("categories"):
                        categories = book.get("categories", [])
                        if isinstance(categories, list):
                            st.caption(f"Tags: {', '.join(categories[:4])}")
                    
                    if book.get("comment"):
                        st.write(f"💭 {book.get('comment')}")
                    
                    # Comment input
                    new_comment = st.text_input(
                        "Add a comment...",
                        value=book.get("comment", ""),
                        key=f"comment_{idx}"
                    )
                    if new_comment != book.get("comment"):
                        library[idx]["comment"] = new_comment
                        save_library(library)
                
                st.divider()

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #999; font-size: 0.9rem;">'
    'LIRIA - AI Literary Advisor | Powered by Streamlit'
    '</p>',
    unsafe_allow_html=True
)

