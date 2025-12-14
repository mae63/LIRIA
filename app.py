"""LIRIA - AI Literary Advisor
Streamlit application with dark theme matching the original React UI.
"""

import streamlit as st
import requests
from typing import List, Dict, Optional
import os
from api_client import (
    sign_up, sign_in, sign_out,
    get_library, add_to_library, update_library_entry, delete_library_entry,
    get_wishlist, add_to_wishlist_api, remove_from_wishlist as api_remove_from_wishlist,
    get_latest_conversation, create_conversation, add_message,
    migrate_localstorage, send_chat_message as api_send_chat_message
)

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="LIRIA - AI Literary Advisor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern SaaS-style CSS
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Style header to be minimal */
    header {
        background: transparent !important;
        border-bottom: none !important;
        padding: 0.5rem !important;
    }
    
    /* Hide header decoration */
    header .stDecoration {display: none;}
    
    /* Hide sidebar collapse button - sidebar should always be visible */
    [data-testid="stSidebarCollapseButton"],
    button[kind="header"][data-testid="baseButton-header"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Main background */
    .stApp {
        background: radial-gradient(circle at top, #1d4ed8 0, transparent 55%), 
                    radial-gradient(circle at bottom, #7c3aed 0, #020617 55%);
        min-height: 100vh;
    }
    
    /* Sidebar styling - always visible */
    [data-testid="stSidebar"] {
        background: rgba(2, 6, 23, 0.95);
        border-right: 1px solid rgba(148, 163, 184, 0.1);
        padding: 24px 16px;
        min-width: 250px !important;
    }
    
    /* Force sidebar to always be visible and prevent collapsing */
    [data-testid="stSidebar"][aria-expanded="false"] {
        display: block !important;
        visibility: visible !important;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        padding-left: 4rem;
        padding-right: 4rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Hide empty containers */
    .element-container {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    
    .dark-card:empty,
    [data-testid="stMarkdownContainer"] .dark-card:empty {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    [class*="st-emotion-cache"]:empty {
        display: none !important;
        height: 0 !important;
    }
    
    /* Typography */
    .main-header {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 12px;
        letter-spacing: -0.02em;
        color: #ffffff;
        text-align: center;
        line-height: 1.2;
    }
    
    .subtitle {
        font-size: 15px;
        line-height: 1.6;
        color: #94a3b8;
        width: 100%;
        margin: 0 auto 40px;
        text-align: center;
        font-weight: 400;
    }
    
    /* Card styling */
    .dark-card {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.12);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        padding: 32px;
        backdrop-filter: blur(20px);
        margin: 0 auto;
        max-width: 900px;
    }
    
    /* Chat container */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 16px;
        max-height: 600px;
        overflow-y: auto;
        padding: 16px;
        margin-bottom: 24px;
        background: rgba(15, 23, 42, 0.4);
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    /* Chat messages */
    .chat-message-user {
        background: rgba(30, 64, 175, 0.3);
        color: #ffffff;
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 14px 18px;
        margin: 8px 0;
        margin-left: auto;
        margin-right: 0;
        max-width: 75%;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        line-height: 1.6;
        font-size: 15px;
    }
    
    .chat-message-assistant {
        background: rgba(15, 23, 42, 0.6);
        color: #e2e8f0;
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 12px;
        padding: 14px 18px;
        margin: 8px 0;
        margin-left: 0;
        margin-right: auto;
        max-width: 75%;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        line-height: 1.6;
        font-size: 15px;
    }
    
    /* Book styling */
    .book-title {
        font-weight: 600;
        color: #ffffff;
        font-size: 16px;
        margin-bottom: 4px;
        line-height: 1.4;
    }
    
    .book-author {
        font-size: 14px;
        color: #cbd5e1;
        margin-bottom: 8px;
        line-height: 1.4;
    }
    
    .book-description {
        font-size: 14px;
        color: #94a3b8;
        margin-top: 8px;
        line-height: 1.6;
    }
    
    /* See more button styling - looks like inline text */
    .see-more-button {
        font-size: 14px !important;
        color: #94a3b8 !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        text-decoration: underline !important;
        font-weight: bold !important;
        box-shadow: none !important;
        min-height: auto !important;
        height: auto !important;
        line-height: 1.6 !important;
        display: inline !important;
    }
    
    .see-more-button:hover {
        color: #cbd5e1 !important;
        background: transparent !important;
        transform: none !important;
    }
    
    .book-categories {
        font-size: 12px;
        color: #64748b;
        margin-top: 8px;
    }
    
    .book-separator {
        height: 1px;
        background: rgba(255, 255, 255, 0.2);
        margin: 16px 0;
        border: none;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background-color: rgba(15, 23, 42, 0.6);
        color: #e2e8f0;
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 15px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        outline: none;
        background-color: rgba(15, 23, 42, 0.8);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #64748b;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #f97316, #fb923c);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
        min-height: 48px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #fb923c, #fdba74);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        transform: translateY(-1px);
    }
    
    /* Add button - orange style */
    .add-button-wrapper .stButton > button {
        background: linear-gradient(135deg, #f97316, #fb923c) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        min-height: 40px !important;
        width: 100% !important;
    }
    
    .add-button-wrapper .stButton > button:hover {
        background: linear-gradient(135deg, #fb923c, #fdba74) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Star buttons */
    button[kind="secondary"] {
        background: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
        font-size: 20px !important;
        padding: 4px 2px !important;
        min-height: auto !important;
        box-shadow: none !important;
        margin: 0 !important;
    }
    
    button[kind="secondary"]:hover {
        color: #cbd5e1 !important;
    }
    
    /* Rating stars - rapprochées */
    [data-testid="column"]:has(button[kind="secondary"]) {
        padding-left: 2px !important;
        padding-right: 2px !important;
    }
    
    /* Empty state */
    .empty-state {
        font-size: 14px;
        color: #94a3b8;
        padding: 24px;
        border-radius: 12px;
        border: 1px dashed rgba(148, 163, 184, 0.3);
        background: rgba(15, 23, 42, 0.4);
        text-align: center;
        line-height: 1.6;
    }
    
    /* Scrollbar */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.3);
        border-radius: 4px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: rgba(148, 163, 184, 0.3);
        border-radius: 4px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: rgba(148, 163, 184, 0.5);
    }
    
    /* Recommended books panel */
    .recommended-books-panel {
        background: transparent;
        border-radius: 12px;
        padding: 16px 0;
        max-height: calc(100vh - 200px);
        overflow-y: auto;
        border: none;
    }
    
    .recommended-book-card {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        position: relative;
    }
    
    .book-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
    }
    
    .book-card-title {
        font-weight: 600;
        color: #ffffff;
        font-size: 14px;
        line-height: 1.4;
        flex: 1;
        margin-right: 8px;
    }
    
    .book-card-close {
        background: transparent;
        border: none;
        color: #94a3b8;
        font-size: 18px;
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
    }
    
    .book-card-close:hover {
        background: rgba(148, 163, 184, 0.2);
        color: #ffffff;
    }
    
    .book-card-author {
        font-size: 12px;
        color: #cbd5e1;
        margin-bottom: 8px;
    }
    
    .book-card-actions {
        display: flex;
        gap: 8px;
        margin-top: 8px;
    }
    
    .book-card-button {
        flex: 1;
        padding: 6px 12px;
        border-radius: 8px;
        border: none;
        font-size: 12px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .book-card-button-wishlist {
        background: rgba(30, 64, 175, 0.3);
        color: #ffffff;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }
    
    .book-card-button-wishlist:hover {
        background: rgba(30, 64, 175, 0.5);
    }
    
    .book-card-button-view {
        background: rgba(249, 115, 22, 0.3);
        color: #ffffff;
        border: 1px solid rgba(249, 115, 22, 0.3);
    }
    
    .book-card-button-view:hover {
        background: rgba(249, 115, 22, 0.5);
    }
    
    .recommended-books-title {
        font-size: 18px;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 16px;
        text-align: center;
    }
    
    .no-recommendations {
        text-align: center;
        color: #94a3b8;
        font-size: 14px;
        padding: 24px;
    }
    
    /* Auth page styles - compacted to fit without scroll */
    .auth-container {
        display: flex;
        justify-content: center;
        align-items: flex-start;
        padding: 0 20px;
        margin-top: 0;
    }
    
    .auth-card {
        background: rgba(15, 23, 42, 0.95);
        border-radius: 20px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        padding: 24px 32px 20px 32px;
        max-width: 400px;
        width: 100%;
        backdrop-filter: blur(20px);
    }
    
    .auth-title {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
    }
    
    .auth-subtitle {
        font-size: 13px;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 16px;
        line-height: 1.4;
    }
    
    /* Style tabs in auth page - compacted */
    .auth-card .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: transparent;
        margin-bottom: 12px;
    }
    
    .auth-card .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
        font-size: 13px;
        padding: 6px 14px;
        border-radius: 8px;
        background: transparent;
    }
    
    .auth-card .stTabs [aria-selected="true"] {
        color: #ffffff;
        background: rgba(30, 64, 175, 0.2);
    }
    
    /* Style form inputs in auth page - compacted */
    .auth-card .stTextInput > div > div > input {
        background-color: rgba(15, 23, 42, 0.8);
        color: #e2e8f0;
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 8px 14px;
        font-size: 14px;
    }
    
    .auth-card .stTextInput > div > div > input:focus {
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        outline: none;
        background-color: rgba(15, 23, 42, 0.9);
    }
    
    .auth-card .stTextInput {
        margin-bottom: 8px;
    }
    
    .auth-card .stForm {
        margin-top: 0;
    }
    
    .auth-card .stButton {
        margin-top: 6px;
    }
    
    .auth-card .stButton > button {
        padding: 8px 24px;
        font-size: 14px;
        min-height: 36px;
    }
    
    /* User menu in top right */
    .user-menu-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
    }
    
    .user-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-weight: 600;
        font-size: 16px;
        cursor: pointer;
        border: 2px solid rgba(148, 163, 184, 0.2);
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .user-avatar:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .user-dropdown {
        position: absolute;
        top: 50px;
        right: 0;
        background: rgba(15, 23, 42, 0.98);
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        padding: 8px;
        min-width: 200px;
        backdrop-filter: blur(20px);
    }
    
    .user-dropdown-item {
        padding: 12px 16px;
        color: #e2e8f0;
        font-size: 14px;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.2s;
    }
    
    .user-dropdown-item:hover {
        background: rgba(148, 163, 184, 0.1);
    }
    
    .user-dropdown-email {
        padding: 12px 16px;
        color: #94a3b8;
        font-size: 13px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        margin-bottom: 4px;
    }
    
    .user-dropdown-signout {
        padding: 12px 16px;
        color: #ef4444;
        font-size: 14px;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.2s;
    }
    
    .user-dropdown-signout:hover {
        background: rgba(239, 68, 68, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None  # {user_id, email, access_token, refresh_token}
if "library" not in st.session_state:
    st.session_state.library = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hi, I'm LIRIA. Tell me what kind of book you're looking for."}
    ]
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "pending_chat_message" not in st.session_state:
    st.session_state.pending_chat_message = None
if "expanded_descriptions" not in st.session_state:
    st.session_state.expanded_descriptions = {}
if "recommended_books" not in st.session_state:
    st.session_state.recommended_books = []
if "wishlist" not in st.session_state:
    st.session_state.wishlist = []
if "dismissed_books" not in st.session_state:
    st.session_state.dismissed_books = []
if "migration_done" not in st.session_state:
    st.session_state.migration_done = False
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False


def get_access_token() -> Optional[str]:
    """Get access token from session state"""
    if st.session_state.user:
        return st.session_state.user.get("access_token")
    return None




def render_auth_page():
    """Render the dedicated authentication page"""
    # Hide header and footer, center content
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
    }
    header {
        visibility: hidden;
        height: 0;
    }
    footer {
        visibility: hidden;
        height: 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="auth-container">
        <div class="auth-card">
            <h1 class="auth-title">Welcome to LIRIA</h1>
            <p class="auth-subtitle">Sign in to access your personal literary advisor.</p>
    """, unsafe_allow_html=True)
    
    # Tabs for Sign In / Sign Up
    auth_tab1, auth_tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with auth_tab1:
        with st.form(key="signin_form", clear_on_submit=False):
            signin_email = st.text_input("Email", key="signin_email")
            signin_password = st.text_input("Password", type="password", key="signin_password")
            signin_submit = st.form_submit_button("Sign In", type="primary", use_container_width=True)
            
            if signin_submit:
                result = sign_in(signin_email, signin_password)
                if result.get("success"):
                    st.session_state.user = {
                        "user_id": result.get("user_id"),
                        "email": result.get("email"),
                        "access_token": result.get("access_token"),
                        "refresh_token": result.get("refresh_token"),
                    }
                    st.session_state.data_loaded = False
                    st.rerun()
                else:
                    st.error(result.get("error", "Sign in failed"))
    
    with auth_tab2:
        with st.form(key="signup_form", clear_on_submit=False):
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            signup_submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)
            
            if signup_submit:
                result = sign_up(signup_email, signup_password)
                if result.get("success"):
                    st.session_state.user = {
                        "user_id": result.get("user_id"),
                        "email": result.get("email"),
                        "access_token": result.get("access_token"),
                        "refresh_token": result.get("refresh_token"),
                    }
                    st.session_state.data_loaded = False
                    st.success("Account created! You are now signed in.")
                    st.rerun()
                else:
                    st.error(result.get("error", "Sign up failed"))
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)


def load_library():
    """Load library from API or session state"""
    if st.session_state.user and not st.session_state.data_loaded:
        # Load from API
        access_token = get_access_token()
        library = get_library(access_token)
        st.session_state.library = library
        st.session_state.data_loaded = True
    return st.session_state.library


def save_library(library):
    """Save library to session state (API calls are made separately)"""
    st.session_state.library = library


def add_book_to_library(book: Dict) -> bool:
    """Add a book to the library via API"""
    access_token = get_access_token()
    if access_token:
        # Use API
        return add_to_library(book, access_token)
    else:
        # Fallback to session state (no auth)
        library = load_library()
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


def update_book_rating(book_id: int, rating: int):
    """Update rating for a book in the library via API"""
    access_token = get_access_token()
    if access_token:
        # Use API
        update_library_entry(book_id, {"rating": rating}, access_token)
        # Refresh library
        st.session_state.data_loaded = False
    else:
        # Fallback to session state
        library = load_library()
        for book in library:
            if book.get("id") == book_id:
                book["rating"] = rating
                save_library(library)
                break


def send_chat_message(message: str, history: List[Dict] = None) -> Optional[Dict]:
    """Send a message to the chat backend with conversation history"""
    access_token = get_access_token()
    
    # Prepare history in the format expected by backend
    history_payload = []
    if history:
        for msg in history:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                history_payload.append({"role": msg["role"], "content": msg["content"]})
    
    # Use API client
    result = api_send_chat_message(message, history_payload, access_token)
    return result


def load_wishlist():
    """Load wishlist from API or session state"""
    if st.session_state.user and not st.session_state.data_loaded:
        # Load from API
        access_token = get_access_token()
        wishlist = get_wishlist(access_token)
        st.session_state.wishlist = wishlist
    return st.session_state.wishlist


def save_wishlist(wishlist):
    """Save wishlist to session state (API calls are made separately)"""
    st.session_state.wishlist = wishlist


def add_to_wishlist(book: Dict) -> bool:
    """Add a book to the wishlist via API"""
    access_token = get_access_token()
    if access_token:
        # Use API
        book_payload = {
            "id": book.get("id", ""),
            "title": book.get("title", ""),
            "author": book.get("author", ""),
            "description": book.get("description", ""),
            "categories": book.get("categories", []),
            "thumbnail": book.get("thumbnail", ""),
            "source": book.get("source", ""),
            "preview_link": book.get("preview_link", ""),
        }
        return add_to_wishlist_api(book_payload, access_token)
    else:
        # Fallback to session state
        wishlist = load_wishlist()
        existing = next(
            (b for b in wishlist if b.get("title") == book.get("title") and 
             b.get("author") == book.get("author")), None
        )
        if not existing:
            book_entry = {
                "id": book.get("id", ""),
                "title": book.get("title", ""),
                "author": book.get("author", ""),
                "description": book.get("description", ""),
                "categories": book.get("categories", []),
                "thumbnail": book.get("thumbnail", ""),
                "source": book.get("source", ""),
                "preview_link": book.get("preview_link", ""),
            }
            wishlist.append(book_entry)
            save_wishlist(wishlist)
            return True
        return False


def remove_from_wishlist(entry_id: int):
    """Remove a book from the wishlist via API"""
    access_token = get_access_token()
    if access_token:
        # Use API
        api_remove_from_wishlist(entry_id, access_token)
        # Refresh wishlist
        st.session_state.data_loaded = False
    else:
        # Fallback to session state
        wishlist = load_wishlist()
        st.session_state.wishlist = [b for b in wishlist if b.get("id") != entry_id]
        save_wishlist(st.session_state.wishlist)


def generate_amazon_url(title: str, author: str = "") -> str:
    """Generate Amazon search URL for a book"""
    from urllib.parse import quote_plus
    
    # Build search query: title + author if available
    if author:
        search_query = f"{title} {author}"
    else:
        search_query = title
    
    # URL encode the search query
    encoded_query = quote_plus(search_query)
    
    # Amazon search URL
    return f"https://www.amazon.com/s?k={encoded_query}&i=stripbooks"


def search_books_direct(query: str, limit: int = 20) -> List[Dict]:
    """Direct search using Google Books and OpenLibrary"""
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
    except Exception:
        pass
    
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
    except Exception:
        pass
    
    # Deduplicate
    seen = set()
    unique_results = []
    for book in results:
        key = f"{book.get('title', '').lower()}|{','.join(book.get('authors', [])).lower()}"
        if key not in seen:
            seen.add(key)
            unique_results.append(book)
    
    return unique_results[:limit]


# Authentication guard: Check if user is authenticated
if not st.session_state.user:
    # Hide sidebar for unauthenticated users
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show only the auth page
    render_auth_page()
    st.stop()  # Stop execution here, don't render the rest of the app

# User is authenticated - show sidebar and main app
# Sidebar navigation (only visible for authenticated users)
st.sidebar.markdown("## LIRIA")


# Load user data if authenticated
if st.session_state.user and not st.session_state.data_loaded:
    access_token = get_access_token()
    # Load library and wishlist
    st.session_state.library = get_library(access_token)
    st.session_state.wishlist = get_wishlist(access_token)
    
    # Load conversation history
    conv_data = get_latest_conversation(access_token)
    if conv_data:
        st.session_state.conversation_id = conv_data.get("conversation_id")
        messages = conv_data.get("messages", [])
        if messages:
            st.session_state.chat_history = [
                {"role": msg.get("role"), "content": msg.get("content")}
                for msg in messages
            ]
        else:
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Hi, I'm LIRIA. Tell me what kind of book you're looking for."}
            ]
    else:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hi, I'm LIRIA. Tell me what kind of book you're looking for."}
        ]
    
    # Migrate localStorage data if not done yet
    if not st.session_state.migration_done:
        # Check if there's any localStorage data to migrate (we'll use session state as fallback)
        old_library = st.session_state.get("old_library", [])
        old_wishlist = st.session_state.get("old_wishlist", [])
        if old_library or old_wishlist:
            migrate_result = migrate_localstorage(old_library, old_wishlist, access_token)
            if migrate_result.get("success"):
                st.session_state.migration_done = True
                # Reload data
                st.session_state.library = get_library(access_token)
                st.session_state.wishlist = get_wishlist(access_token)
        else:
            st.session_state.migration_done = True
    
    st.session_state.data_loaded = True

page = st.sidebar.radio(
    "Navigation",
    ["Chat", "Search", "My Library"],
    index=0
)
st.sidebar.markdown(f"**Library:** {len(load_library())} books")
st.sidebar.markdown(f"**Wishlist:** {len(load_wishlist())} books")

# Main content based on selected page
if page == "Chat":
    st.markdown('<h1 class="main-header">LIRIA — Chat</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p class="subtitle">
        Describe your mood, your favorite authors, or a recent book. 
        LIRIA will suggest titles and help you build your long‑term reading profile.
    </p>
    """, unsafe_allow_html=True)
    
    # Create two columns: 70% chat, 30% recommendations (agrandi pour que les boutons soient sur la même ligne)
    chat_col, rec_col = st.columns([2.3, 1], gap="medium")
    
    with chat_col:
        # Chat conversation
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-message-user">{msg["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-message-assistant">{msg["content"]}</div>',
                    unsafe_allow_html=True
                )
        
        # Chat input form
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([5, 1], gap="medium")
            with col1:
                user_input = st.text_input(
                    "",
                    key="chat_input",
                    label_visibility="collapsed",
                    placeholder="Ask LIRIA for a recommendation..."
                )
            with col2:
                send_button = st.form_submit_button("Send", type="primary", use_container_width=True)
    
    with rec_col:
        # Recommended Books Panel
        st.markdown('<div class="recommended-books-title">Recommended Books</div>', unsafe_allow_html=True)
        st.markdown('<div class="recommended-books-panel">', unsafe_allow_html=True)
        
        # Extract books mentioned in the last assistant message
        mentioned_book_ids = set()
        if st.session_state.chat_history:
            last_assistant_msg = None
            for msg in reversed(st.session_state.chat_history):
                if msg.get("role") == "assistant":
                    last_assistant_msg = msg.get("content", "").lower()
                    break
            
            if last_assistant_msg:
                # Check which books from recommended_books are mentioned in the chat
                for book in st.session_state.recommended_books:
                    book_title = book.get("title", "").lower()
                    book_author = book.get("author", "").lower()
                    
                    # Check if full title is mentioned
                    if book_title and book_title in last_assistant_msg:
                        mentioned_book_ids.add(book.get("id"))
                        continue
                    
                    # Check if author is mentioned
                    if book_author and book_author in last_assistant_msg:
                        mentioned_book_ids.add(book.get("id"))
                        continue
                    
                    # Check for partial title matches (first 2-3 significant words)
                    title_words = [w for w in book_title.split() if len(w) > 3][:3]
                    if title_words and any(word in last_assistant_msg for word in title_words):
                        mentioned_book_ids.add(book.get("id"))
                        continue
                    
                    # Check for author first name or last name
                    if book_author:
                        author_parts = book_author.split(",")
                        for part in author_parts:
                            part = part.strip().lower()
                            if len(part) > 3 and part in last_assistant_msg:
                                mentioned_book_ids.add(book.get("id"))
                                break
        
        # Filter: only show books that are mentioned in chat AND not dismissed
        active_books = [
            b for b in st.session_state.recommended_books 
            if b.get("id") not in st.session_state.dismissed_books
            and (b.get("id") in mentioned_book_ids if mentioned_book_ids else False)
        ]
        
        if active_books:
            for book in active_books:
                book_id = book.get("id", "")
                book_title = book.get("title", "Unknown")
                book_author = book.get("author", "Unknown Author")
                book_thumbnail = book.get("thumbnail", "")
                preview_link = book.get("preview_link", "")
                if not preview_link:
                    preview_link = f"https://www.google.com/search?q={book_title.replace(' ', '+')}+{book_author.replace(' ', '+')}"
                
                # Create book card with cover image
                cover_col, info_col = st.columns([1, 2], gap="small")
                with cover_col:
                    if book_thumbnail:
                        st.image(book_thumbnail, width=60)
                    else:
                        st.markdown('<div style="width: 60px; height: 90px; background: rgba(148, 163, 184, 0.2); border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #94a3b8; font-size: 10px;">No cover</div>', unsafe_allow_html=True)
                
                with info_col:
                    st.markdown(f'''
                    <div class="recommended-book-card">
                        <div class="book-card-header">
                            <div class="book-card-title">{book_title}</div>
                        </div>
                        <div class="book-card-author">by {book_author}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Action buttons row - ajusté pour que "Wishlist" et "View" soient sur la même ligne
                    btn_col1, btn_col2, btn_col3 = st.columns([1, 2.5, 2.5], gap="small")
                    with btn_col1:
                        if st.button("✖", key=f"dismiss_{book_id}", help="Dismiss", use_container_width=True):
                            if book_id not in st.session_state.dismissed_books:
                                st.session_state.dismissed_books.append(book_id)
                            st.rerun()
                    with btn_col2:
                        if st.button("Wishlist", key=f"wishlist_{book_id}", help="Add to Wishlist", use_container_width=True):
                            if add_to_wishlist(book):
                                # Reload wishlist from API to update the UI immediately
                                access_token = get_access_token()
                                st.session_state.wishlist = get_wishlist(access_token)
                                st.success(f"Added to wishlist!")
                            else:
                                st.info("Already in wishlist")
                            st.rerun()
                    with btn_col3:
                        st.link_button("View", preview_link, use_container_width=True)
        else:
            st.markdown('<div class="no-recommendations">No recommendations yet. Start chatting with LIRIA!</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle new user message
    if send_button and user_input:
        user_message = user_input.strip()
        if user_message:
            # Create conversation if needed (for authenticated users)
            access_token = get_access_token()
            if access_token and not st.session_state.conversation_id:
                conv_id = create_conversation(access_token)
                if conv_id:
                    st.session_state.conversation_id = conv_id
            
            st.session_state.chat_history.append({"role": "user", "content": user_message})
            st.session_state.pending_chat_message = user_message
            st.rerun()
    
    # Process AI response
    if st.session_state.pending_chat_message is not None:
        pending_msg = st.session_state.pending_chat_message
        st.session_state.pending_chat_message = None
        
        # Save user message to database if authenticated
        access_token = get_access_token()
        if access_token and st.session_state.conversation_id:
            add_message(st.session_state.conversation_id, "user", pending_msg, access_token)
        
        # Send conversation history (all messages except the current one which is being processed)
        history = st.session_state.chat_history[:-1] if len(st.session_state.chat_history) > 0 else []
        
        with st.spinner("LIRIA is thinking..."):
            response = send_chat_message(pending_msg, history=history)
        
        if response:
            reply = response.get("reply", "I couldn't generate a response.")
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            
            # Save assistant message to database if authenticated
            if access_token and st.session_state.conversation_id:
                add_message(st.session_state.conversation_id, "assistant", reply, access_token)
            
            # Extract books mentioned in the reply
            books = response.get("books", [])
            reply_lower = reply.lower()
            
            # Clear previous recommendations and only keep books mentioned in this reply
            mentioned_books = []
            if books:
                for book in books:
                    book_title = book.get("title", "").lower()
                    book_author = book.get("author", "").lower()
                    
                    # Check if the book is mentioned in the reply
                    title_mentioned = book_title and book_title in reply_lower
                    author_mentioned = book_author and book_author in reply_lower
                    
                    # Also check for partial matches (first few words of title)
                    title_words = book_title.split()[:3]  # First 3 words
                    title_partial_mentioned = any(word in reply_lower for word in title_words if len(word) > 3)
                    
                    if title_mentioned or author_mentioned or title_partial_mentioned:
                        # Convert BookResponse format to our format
                        preview_link = book.get("preview_link", "")
                        if not preview_link:
                            # Fallback: construct URL if not provided
                            if book.get("id", "").startswith("google:"):
                                preview_link = f"https://books.google.com/books?id={book.get('id', '').replace('google:', '')}"
                            else:
                                preview_link = f"https://www.google.com/search?q={book.get('title', '').replace(' ', '+')}+{book.get('author', '').replace(' ', '+')}"
                        
                        book_entry = {
                            "id": book.get("id", ""),
                            "title": book.get("title", ""),
                            "author": book.get("author", ""),
                            "description": book.get("description", ""),
                            "categories": book.get("categories", []),
                            "thumbnail": book.get("thumbnail", ""),
                            "source": book.get("source", ""),
                            "preview_link": preview_link,
                        }
                        mentioned_books.append(book_entry)
            
            # Replace recommended books with only the ones mentioned in this reply
            # Keep previously mentioned books that haven't been dismissed
            existing_ids = {b.get("id") for b in st.session_state.recommended_books}
            for book_entry in mentioned_books:
                if book_entry.get("id") not in existing_ids:
                    st.session_state.recommended_books.append(book_entry)
        else:
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": "Sorry, I couldn't connect to the server. Please make sure the backend is running."
            })
        st.rerun()

elif page == "Search":
    st.markdown('<h1 class="main-header">Search books in real time</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p class="subtitle">
        Live search powered directly by Google Books and OpenLibrary (no backend). 
        Type a title, an author, or a topic to see detailed results with descriptions, 
        then add interesting books to your library.
    </p>
    """, unsafe_allow_html=True)
    
    # Search form
    with st.form(key="search_form", clear_on_submit=False):
        col1, col2 = st.columns([5, 1], gap="medium")
        with col1:
            search_query = st.text_input(
                "Search by title, author, or topic",
                key="search_input",
                label_visibility="collapsed",
                placeholder="e.g. 'Dune', 'Agatha Christie', 'cyberpunk'"
            )
        with col2:
            search_button = st.form_submit_button("Search", type="primary", use_container_width=True)
        
        if search_button and search_query:
            with st.spinner("Searching..."):
                results = search_books_direct(search_query, 20)
                st.session_state.search_results = results
    
    # Display results
    if st.session_state.search_results:
        st.markdown('<div class="dark-card">', unsafe_allow_html=True)
        for book in st.session_state.search_results:
            library = load_library()
            is_added = any(
                b.get("title") == book.get("title") and 
                b.get("authors") == (book.get("authors") if isinstance(book.get("authors"), list) else [book.get("authors")])
                for b in library
            )
            
            col1, col2, col3 = st.columns([1, 4, 1], gap="small")
            
            with col1:
                if book.get("coverUrl"):
                    st.image(book.get("coverUrl"), width=58)
            
            with col2:
                st.markdown(f'<div class="book-title">{book.get("title", "Unknown")}</div>', unsafe_allow_html=True)
                authors = book.get("authors", [])
                if authors:
                    author_str = ', '.join(authors) if isinstance(authors, list) else authors
                    st.markdown(f'<div class="book-author">by {author_str}</div>', unsafe_allow_html=True)
                if book.get("description"):
                    desc = book.get("description", "").strip()
                    if desc:
                        book_id = book.get("id", f"book_{hash(book.get('title', ''))}")
                        is_expanded = st.session_state.expanded_descriptions.get(book_id, False)
                        
                        if len(desc) > 300:
                            if is_expanded:
                                st.markdown(f'<div class="book-description">{desc}</div>', unsafe_allow_html=True)
                                if st.button("see less", key=f"desc_less_{book_id}", use_container_width=False):
                                    st.session_state.expanded_descriptions[book_id] = False
                                    st.rerun()
                            else:
                                desc_short = desc[:300]
                                # Display text with inline "see more" button styled as text
                                st.markdown(f'<div class="book-description" style="display: inline;">{desc_short} </div>', unsafe_allow_html=True)
                                if st.button("see more", key=f"desc_more_{book_id}", use_container_width=False):
                                    st.session_state.expanded_descriptions[book_id] = True
                                    st.rerun()
                                # Style the button to look like inline text (same size, underlined, bold)
                                st.markdown(f'''
                                <style>
                                button[key="desc_more_{book_id}"] {{
                                    font-size: 14px !important;
                                    color: #94a3b8 !important;
                                    background: transparent !important;
                                    border: none !important;
                                    padding: 0 !important;
                                    margin: 0 0 0 4px !important;
                                    text-decoration: underline !important;
                                    font-weight: bold !important;
                                    box-shadow: none !important;
                                    min-height: auto !important;
                                    height: auto !important;
                                    line-height: 1.6 !important;
                                    display: inline !important;
                                    vertical-align: baseline !important;
                                    cursor: pointer !important;
                                }}
                                button[key="desc_more_{book_id}"]:hover {{
                                    color: #cbd5e1 !important;
                                    background: transparent !important;
                                    transform: none !important;
                                }}
                                </style>
                                ''', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="book-description">{desc}</div>', unsafe_allow_html=True)
                if book.get("categories"):
                    categories = book.get("categories", [])
                    if isinstance(categories, list):
                        st.markdown(f'<div class="book-categories">{", ".join(categories[:4])}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size: 11px; color: #64748b; margin-top: 4px;">Source: {book.get("source", "Unknown")}</div>', unsafe_allow_html=True)
            
            with col3:
                # Check if book is in wishlist
                wishlist = load_wishlist()
                is_in_wishlist = any(
                    b.get("title") == book.get("title") and 
                    (b.get("author") == (book.get("authors")[0] if isinstance(book.get("authors"), list) and book.get("authors") else book.get("authors")) or
                     (isinstance(book.get("authors"), list) and len(book.get("authors")) > 0 and b.get("author") == book.get("authors")[0]))
                    for b in wishlist
                )
                
                if not is_added:
                    # Two buttons: Add to Library and Add to Wishlist - alignés verticalement
                    btn_col1, btn_col2 = st.columns(2, gap="small")
                    with btn_col1:
                        st.markdown('<div class="add-button-wrapper" style="display: flex; align-items: center; height: 100%;">', unsafe_allow_html=True)
                        add_btn = st.button("+ Add", key=f"search_add_{book.get('id')}", use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        if add_btn:
                            # Convert search book format to library format
                            library_book = {
                                "title": book.get("title", ""),
                                "authors": book.get("authors", []) if isinstance(book.get("authors"), list) else [],
                                "description": book.get("description", "") or "",
                                "categories": book.get("categories", []) if isinstance(book.get("categories"), list) else [],
                                "source": book.get("source", "") or "",
                                "rawId": book.get("rawId", "") or "",
                                "coverUrl": book.get("coverUrl", "") or "",
                                "rating": 0,
                                "comment": "",
                                "apiRating": book.get("apiRating"),
                                "apiRatingsCount": book.get("apiRatingsCount", 0) or 0,
                            }
                            if add_book_to_library(library_book):
                                # Reload library to update the UI immediately
                                access_token = get_access_token()
                                st.session_state.library = get_library(access_token)
                                st.rerun()
                            else:
                                st.info("Already in library")
                    with btn_col2:
                        if not is_in_wishlist:
                            st.markdown('<div style="display: flex; align-items: center; height: 100%;">', unsafe_allow_html=True)
                            wishlist_btn = st.button("Wishlist", key=f"search_wishlist_{book.get('id')}", use_container_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            if wishlist_btn:
                                # Convert search book format to wishlist format
                                wishlist_book = {
                                    "id": book.get("id", ""),
                                    "title": book.get("title", ""),
                                    "author": ", ".join(book.get("authors", [])) if isinstance(book.get("authors"), list) else str(book.get("authors", "")),
                                    "description": book.get("description", ""),
                                    "categories": book.get("categories", []),
                                    "thumbnail": book.get("coverUrl", ""),
                                    "source": book.get("source", ""),
                                    "preview_link": book.get("previewLink", ""),
                                }
                                if add_to_wishlist(wishlist_book):
                                    # Reload wishlist from API to update the UI immediately
                                    access_token = get_access_token()
                                    st.session_state.wishlist = get_wishlist(access_token)
                                    st.success("Added to wishlist!")
                                    st.rerun()
                                else:
                                    st.info("Already in wishlist")
                        else:
                            st.markdown('<div style="padding: 10px 16px; background: rgba(30, 64, 175, 0.1); border: 1px solid rgba(30, 64, 175, 0.3); border-radius: 12px; color: #60a5fa; font-size: 14px; font-weight: 500; text-align: center; display: flex; align-items: center; height: 100%;">In Wishlist ✓</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="padding: 10px 16px; background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 12px; color: #4ade80; font-size: 14px; font-weight: 500; text-align: center;">Added ✓</div>', unsafe_allow_html=True)
            
            # Separator between books
            if book != st.session_state.search_results[-1]:
                st.markdown('<hr class="book-separator">', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    elif not st.session_state.search_results:
        st.markdown("""
        <div class="empty-state">
            No results yet. Try searching for a specific title ("Dune"), author
            ("Ursula K. Le Guin"), or theme ("space opera"). Results are pulled live from Google Books and OpenLibrary.
        </div>
        """, unsafe_allow_html=True)

elif page == "My Library":
    st.markdown('<h1 class="main-header">My Library</h1>', unsafe_allow_html=True)
    
    # Create tabs for Library and Wishlist
    tab1, tab2 = st.tabs(["Library", "Wishlist"])
    
    with tab1:
        st.markdown("""
        <p class="subtitle">
            A simple reading log for books you have read, with ratings and short
            reflections. LIRIA uses this to understand your long‑term reading taste.
        </p>
        """, unsafe_allow_html=True)
        
        library = load_library()
        
        if not library:
            st.markdown("""
            <div class="empty-state">
                No entries yet. You can add books directly from the search page, or
                manually here by deciding on a title, a rating, and a short comment.
            </div>
            """, unsafe_allow_html=True)
        else:
            # Organize books in a grid: 3 books per row
            for row_start in range(0, len(library), 3):
                row_books = library[row_start:row_start + 3]
                cols = st.columns(3, gap="medium")
                
                for col_idx, book in enumerate(row_books):
                    idx = row_start + col_idx
                    with cols[col_idx]:
                        st.markdown('<div class="dark-card" style="margin-bottom: 24px;">', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([1, 4], gap="small")
                        
                        with col1:
                            if book.get("coverUrl"):
                                st.image(book.get("coverUrl"), width=58)
                        
                        with col2:
                            st.markdown(f'<div class="book-title">{book.get("title", "Unknown")}</div>', unsafe_allow_html=True)
                            if book.get("authors"):
                                authors = book.get("authors", [])
                                if isinstance(authors, list):
                                    st.markdown(f'<div class="book-author">by {", ".join(authors)}</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<div class="book-author">by {authors}</div>', unsafe_allow_html=True)
                            
                            # Rating stars (5 stars) - rapprochées
                            st.markdown('<div style="font-size: 12px; color: #e5e7eb; margin: 4px 0;">Rate this book:</div>', unsafe_allow_html=True)
                            rating_cols = st.columns(5, gap="small")
                            current_rating = book.get("rating", 0)
                            for i, col in enumerate(rating_cols):
                                with col:
                                    star_value = i + 1
                                    star_char = "★" if star_value <= current_rating else "☆"
                                    if st.button(star_char, key=f"rate_{idx}_{star_value}", use_container_width=True):
                                        book_id = book.get("id")
                                        if book_id:
                                            update_book_rating(book_id, star_value)
                                        else:
                                            # Fallback for books without ID
                                            library[idx]["rating"] = star_value
                                            save_library(library)
                                        st.rerun()
                            
                            if book.get("apiRating"):
                                st.markdown(f'<div style="font-size: 11px; color: #64748b; margin-top: 4px;">Community: {book.get("apiRating")}/5 ({book.get("apiRatingsCount", 0)} ratings)</div>', unsafe_allow_html=True)
                            
                            if book.get("categories"):
                                categories = book.get("categories", [])
                                if isinstance(categories, list):
                                    st.markdown(f'<div class="book-categories">{", ".join(categories[:4])}</div>', unsafe_allow_html=True)
                            
                            # Comment input
                            st.markdown('<div style="font-size: 12px; color: #e5e7eb; margin: 8px 0 4px 0;">Comment:</div>', unsafe_allow_html=True)
                            new_comment = st.text_input(
                                "Add a comment...",
                                value=book.get("comment", ""),
                                key=f"comment_{idx}",
                                label_visibility="collapsed"
                            )
                            if new_comment != book.get("comment"):
                                book_id = book.get("id")
                                access_token = get_access_token()
                                if access_token and book_id:
                                    # Update via API
                                    update_library_entry(book_id, {"comment": new_comment}, access_token)
                                    # Refresh library
                                    st.session_state.data_loaded = False
                                else:
                                    # Fallback to session state
                                    library[idx]["comment"] = new_comment
                                    save_library(library)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
        <p class="subtitle">
            Books you've saved from recommendations. Move them to your library when you're ready to read them.
        </p>
        """, unsafe_allow_html=True)
        
        wishlist = load_wishlist()
        
        if not wishlist:
            st.markdown("""
            <div class="empty-state">
                No books in your wishlist yet. Start chatting with LIRIA and add recommended books to your wishlist!
            </div>
            """, unsafe_allow_html=True)
        else:
            # Organize books in a grid: 3 books per row
            for row_start in range(0, len(wishlist), 3):
                row_books = wishlist[row_start:row_start + 3]
                cols = st.columns(3, gap="medium")
                
                for col_idx, book in enumerate(row_books):
                    idx = row_start + col_idx
                    entry_id = book.get("id")
                    
                    with cols[col_idx]:
                        st.markdown('<div class="dark-card" style="margin-bottom: 24px;">', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([1, 4], gap="small")
                        
                        with col1:
                            if book.get("thumbnail"):
                                st.image(book.get("thumbnail"), width=58)
                        
                        with col2:
                            st.markdown(f'<div class="book-title">{book.get("title", "Unknown")}</div>', unsafe_allow_html=True)
                            if book.get("author"):
                                st.markdown(f'<div class="book-author">by {book.get("author")}</div>', unsafe_allow_html=True)
                            
                            if book.get("description"):
                                desc = book.get("description", "").strip()
                                if desc:
                                    st.markdown(f'<div class="book-description">{desc[:200]}{"..." if len(desc) > 200 else ""}</div>', unsafe_allow_html=True)
                            
                            if book.get("categories"):
                                categories = book.get("categories", [])
                                if isinstance(categories, list):
                                    st.markdown(f'<div class="book-categories">{", ".join(categories[:4])}</div>', unsafe_allow_html=True)
                            
                            # Action buttons: Add to Library, Buy on Amazon, and Remove
                            action_col1, action_col2, action_col3 = st.columns(3, gap="small")
                            with action_col1:
                                if st.button("Add to Library", key=f"wishlist_to_lib_{idx}", use_container_width=True):
                                    # Convert wishlist book to library format
                                    library_book = {
                                        "title": book.get("title", ""),
                                        "authors": [book.get("author", "")] if book.get("author") else [],
                                        "description": book.get("description", "") or "",
                                        "categories": book.get("categories", []) if isinstance(book.get("categories"), list) else [],
                                        "source": book.get("source", "") or "",
                                        "rawId": str(book.get("id", "")) or "",
                                        "coverUrl": book.get("thumbnail", "") or "",
                                        "rating": 0,
                                        "comment": "",
                                        "apiRating": book.get("api_rating"),
                                        "apiRatingsCount": book.get("api_ratings_count", 0),
                                    }
                                    if add_book_to_library(library_book):
                                        if entry_id:
                                            remove_from_wishlist(entry_id)
                                        # Reload library to show the new book
                                        access_token = get_access_token()
                                        st.session_state.library = get_library(access_token)
                                        st.success("Added to library!")
                                        st.rerun()
                                    else:
                                        st.info("Already in library")
                            with action_col2:
                                # Generate Amazon URL
                                amazon_url = generate_amazon_url(book.get("title", ""), book.get("author", ""))
                                st.link_button("Buy on Amazon", amazon_url, use_container_width=True)
                            with action_col3:
                                if st.button("Remove", key=f"wishlist_remove_{idx}", use_container_width=True):
                                    if entry_id:
                                        remove_from_wishlist(entry_id)
                                    # Reload wishlist to update UI
                                    access_token = get_access_token()
                                    st.session_state.wishlist = get_wishlist(access_token)
                                    st.rerun()
                        
                        st.markdown('</div>', unsafe_allow_html=True)
