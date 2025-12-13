"""
API client for LIRIA backend.
Handles all API calls for authentication, library, wishlist, and conversations.
"""

import requests
from typing import List, Dict, Optional
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def get_auth_headers(access_token: Optional[str] = None) -> Dict[str, str]:
    """Get authorization headers for API requests"""
    headers = {"Content-Type": "application/json"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


# Authentication functions
def sign_up(email: str, password: str) -> Dict:
    """Sign up a new user"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/signup",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def sign_in(email: str, password: str) -> Dict:
    """Sign in an existing user"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/signin",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def sign_out(access_token: Optional[str] = None) -> bool:
    """Sign out the current user"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/signout",
            headers=get_auth_headers(access_token),
        )
        return response.json().get("success", False)
    except Exception:
        return False


# Library functions
def get_library(access_token: Optional[str] = None) -> List[Dict]:
    """Get user's library from API"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/library",
            headers=get_auth_headers(access_token),
        )
        if response.status_code == 200:
            data = response.json()
            # Convert database format to frontend format
            library = []
            for entry in data.get("library", []):
                library.append({
                    "id": entry.get("id"),
                    "title": entry.get("title", ""),
                    "authors": [a.strip() for a in entry.get("author", "").split(",") if a.strip()] if isinstance(entry.get("author"), str) else (entry.get("author", []) if isinstance(entry.get("author"), list) else []),
                    "description": entry.get("description", ""),
                    "categories": entry.get("categories", []),
                    "source": entry.get("source", ""),
                    "rawId": entry.get("raw_id", ""),
                    "coverUrl": entry.get("cover_url", ""),
                    "rating": entry.get("rating", 0),
                    "comment": entry.get("comment", ""),
                    "apiRating": entry.get("api_rating"),
                    "apiRatingsCount": entry.get("api_ratings_count", 0),
                })
            return library
        elif response.status_code == 503:
            # Database not configured, return empty list
            return []
        else:
            return []
    except Exception as e:
        print(f"[API] Error getting library: {e}")
        return []


def add_to_library(book: Dict, access_token: Optional[str] = None) -> bool:
    """Add a book to user's library via API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/library",
            json=book,
            headers=get_auth_headers(access_token),
        )
        if response.status_code == 200:
            return response.json().get("success", False)
        return False
    except Exception as e:
        print(f"[API] Error adding to library: {e}")
        return False


def update_library_entry(entry_id: int, updates: Dict, access_token: Optional[str] = None) -> bool:
    """Update a library entry via API"""
    try:
        response = requests.put(
            f"{BACKEND_URL}/library/{entry_id}",
            json=updates,
            headers=get_auth_headers(access_token),
        )
        if response.status_code == 200:
            return response.json().get("success", False)
        return False
    except Exception as e:
        print(f"[API] Error updating library entry: {e}")
        return False


def delete_library_entry(entry_id: int, access_token: Optional[str] = None) -> bool:
    """Delete a library entry via API"""
    try:
        response = requests.delete(
            f"{BACKEND_URL}/library/{entry_id}",
            headers=get_auth_headers(access_token),
        )
        if response.status_code == 200:
            return response.json().get("success", False)
        return False
    except Exception as e:
        print(f"[API] Error deleting library entry: {e}")
        return False


# Wishlist functions
def get_wishlist(access_token: Optional[str] = None) -> List[Dict]:
    """Get user's wishlist from API"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/wishlist",
            headers=get_auth_headers(access_token),
        )
        if response.status_code == 200:
            data = response.json()
            # Convert database format to frontend format
            wishlist = []
            for entry in data.get("wishlist", []):
                wishlist.append({
                    "id": entry.get("id"),
                    "title": entry.get("title", ""),
                    "author": entry.get("author", ""),
                    "description": entry.get("description", ""),
                    "categories": entry.get("categories", []),
                    "thumbnail": entry.get("thumbnail", ""),
                    "source": entry.get("source", ""),
                    "preview_link": entry.get("preview_link", ""),
                    "book_id": entry.get("book_id", ""),
                })
            return wishlist
        elif response.status_code == 503:
            # Database not configured, return empty list
            return []
        else:
            return []
    except Exception as e:
        print(f"[API] Error getting wishlist: {e}")
        return []


def add_to_wishlist_api(book: Dict, access_token: Optional[str] = None) -> bool:
    """Add a book to user's wishlist via API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/wishlist",
            json=book,
            headers=get_auth_headers(access_token),
        )
        if response.status_code == 200:
            return response.json().get("success", False)
        return False
    except Exception as e:
        print(f"[API] Error adding to wishlist: {e}")
        return False


def remove_from_wishlist(entry_id: int, access_token: Optional[str] = None) -> bool:
    """Remove a book from user's wishlist via API"""
    try:
        response = requests.delete(
            f"{BACKEND_URL}/wishlist/{entry_id}",
            headers=get_auth_headers(access_token),
        )
        if response.status_code == 200:
            return response.json().get("success", False)
        return False
    except Exception as e:
        print(f"[API] Error removing from wishlist: {e}")
        return False


# Conversation functions
def get_latest_conversation(access_token: Optional[str] = None) -> Optional[Dict]:
    """Get user's latest conversation with messages from API"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/conversations/latest",
            headers=get_auth_headers(access_token),
        )
        if response.status_code == 200:
            data = response.json()
            conversation = data.get("conversation")
            messages = data.get("messages", [])
            if conversation:
                return {
                    "conversation_id": conversation.get("id"),
                    "messages": messages,
                }
            return None
        elif response.status_code == 503:
            # Database not configured
            return None
        else:
            return None
    except Exception as e:
        print(f"[API] Error getting latest conversation: {e}")
        return None


def create_conversation(access_token: Optional[str] = None) -> Optional[int]:
    """Create a new conversation via API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/conversations",
            headers=get_auth_headers(access_token),
        )
        if response.status_code == 200:
            return response.json().get("conversation_id")
        return None
    except Exception as e:
        print(f"[API] Error creating conversation: {e}")
        return None


def add_message(conversation_id: int, role: str, content: str, access_token: Optional[str] = None) -> bool:
    """Add a message to a conversation via API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/conversations/{conversation_id}/messages",
            json={"role": role, "content": content},
            headers=get_auth_headers(access_token),
        )
        if response.status_code == 200:
            return response.json().get("success", False)
        return False
    except Exception as e:
        print(f"[API] Error adding message: {e}")
        return False


# Migration function
def migrate_localstorage(library: List[Dict], wishlist: List[Dict], access_token: Optional[str] = None) -> Dict:
    """Migrate localStorage data to database"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/migrate/localstorage",
            json={"library": library, "wishlist": wishlist},
            headers=get_auth_headers(access_token),
        )
        if response.status_code == 200:
            return response.json()
        return {"success": False, "error": "Migration failed"}
    except Exception as e:
        print(f"[API] Error migrating data: {e}")
        return {"success": False, "error": str(e)}


# Chat function (modified to include authorization)
def send_chat_message(message: str, history: List[Dict], access_token: Optional[str] = None) -> Dict:
    """Send a chat message to the backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": message, "history": history},
            headers=get_auth_headers(access_token),
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"reply": "Error: Could not get response from LIRIA.", "books": []}
    except Exception as e:
        print(f"[API] Error sending chat message: {e}")
        return {"reply": "Error: Could not connect to LIRIA.", "books": []}

