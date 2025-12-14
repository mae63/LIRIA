"""
Database service for Supabase integration.
Handles all database operations for users, library, wishlist, and conversations.
"""

import os
from typing import List, Dict, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import httpx

load_dotenv()

class DatabaseService:
    """Service for database operations using Supabase"""
    
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.supabase_url = supabase_url
        self.supabase_anon_key = supabase_key
    
    def _get_client_with_token(self, access_token: str) -> Client:
        """Create a Supabase client with user's access token for RLS"""
        # Create a new client and set the session with the access token
        client = create_client(self.supabase_url, self.supabase_anon_key)
        try:
            # Try to set session with access token (refresh_token can be empty for RLS)
            client.auth.set_session(access_token, "")
        except Exception:
            # If set_session fails, the client will still work but RLS might not
            pass
        return client
    
    # Library operations
    def get_user_library(self, user_id: str, access_token: Optional[str] = None) -> List[Dict]:
        """Get all library entries for a user"""
        try:
            # Use client with user's access token for RLS to work
            client = self._get_client_with_token(access_token) if access_token else self.supabase
            response = client.table("library_entries").select("*").eq("user_id", user_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"[DatabaseService] Error getting library: {e}")
            return []
    
    def add_to_library(self, user_id: str, book: Dict, access_token: Optional[str] = None) -> bool:
        """Add a book to user's library"""
        try:
            # Use client with user's access token for RLS to work
            client = self._get_client_with_token(access_token) if access_token else self.supabase
            
            # Convert authors list to string for storage
            authors = book.get("authors", [])
            author_str = ", ".join(authors) if isinstance(authors, list) else str(authors)
            
            # Check if book already exists (normalize title and author for comparison)
            title = book.get("title", "").strip().lower()
            # Get all existing books for this user to compare
            all_books = client.table("library_entries").select("*").eq("user_id", user_id).execute()
            if all_books.data:
                for existing_book in all_books.data:
                    existing_title = existing_book.get("title", "").strip().lower()
                    existing_author = existing_book.get("author", "").strip().lower()
                    if existing_title == title and existing_author == author_str.strip().lower():
                        return False
            
            entry = {
                "user_id": user_id,
                "title": book.get("title", ""),
                "author": author_str,
                "description": book.get("description", ""),
                "categories": book.get("categories", []),
                "source": book.get("source", ""),
                "raw_id": book.get("rawId", ""),
                "cover_url": book.get("coverUrl", ""),
                "rating": book.get("rating", 0),
                "comment": book.get("comment", ""),
                "api_rating": book.get("apiRating"),
                "api_ratings_count": book.get("apiRatingsCount", 0),
            }
            client.table("library_entries").insert(entry).execute()
            return True
        except Exception as e:
            print(f"[DatabaseService] Error adding to library: {e}")
            return False
    
    def update_library_entry(self, user_id: str, entry_id: int, updates: Dict, access_token: Optional[str] = None) -> bool:
        """Update a library entry"""
        try:
            # Use client with user's access token for RLS to work
            client = self._get_client_with_token(access_token) if access_token else self.supabase
            client.table("library_entries").update(updates).eq("id", entry_id).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"[DatabaseService] Error updating library entry: {e}")
            return False
    
    def delete_library_entry(self, user_id: str, entry_id: int, access_token: Optional[str] = None) -> bool:
        """Delete a library entry"""
        try:
            # Use client with user's access token for RLS to work
            client = self._get_client_with_token(access_token) if access_token else self.supabase
            client.table("library_entries").delete().eq("id", entry_id).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"[DatabaseService] Error deleting library entry: {e}")
            return False
    
    # Wishlist operations
    def get_user_wishlist(self, user_id: str, access_token: Optional[str] = None) -> List[Dict]:
        """Get all wishlist entries for a user"""
        try:
            # Use client with user's access token for RLS to work
            client = self._get_client_with_token(access_token) if access_token else self.supabase
            response = client.table("wishlist_entries").select("*").eq("user_id", user_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"[DatabaseService] Error getting wishlist: {e}")
            return []
    
    def add_to_wishlist(self, user_id: str, book: Dict, access_token: Optional[str] = None) -> bool:
        """Add a book to user's wishlist"""
        try:
            # Use client with user's access token for RLS to work
            client = self._get_client_with_token(access_token) if access_token else self.supabase
            
            # Check if book already exists
            existing = client.table("wishlist_entries").select("*").eq("user_id", user_id).eq("title", book.get("title", "")).eq("author", book.get("author", "")).execute()
            if existing.data:
                return False
            
            entry = {
                "user_id": user_id,
                "title": book.get("title", ""),
                "author": book.get("author", ""),
                "description": book.get("description", ""),
                "categories": book.get("categories", []),
                "thumbnail": book.get("thumbnail", ""),
                "source": book.get("source", ""),
                "preview_link": book.get("preview_link", ""),
                "book_id": book.get("id", ""),
            }
            client.table("wishlist_entries").insert(entry).execute()
            return True
        except Exception as e:
            print(f"[DatabaseService] Error adding to wishlist: {e}")
            return False
    
    def remove_from_wishlist(self, user_id: str, entry_id: int, access_token: Optional[str] = None) -> bool:
        """Remove a book from user's wishlist"""
        try:
            # Use client with user's access token for RLS to work
            client = self._get_client_with_token(access_token) if access_token else self.supabase
            client.table("wishlist_entries").delete().eq("id", entry_id).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"[DatabaseService] Error removing from wishlist: {e}")
            return False
    
    # Conversation operations
    def get_user_conversations(self, user_id: str) -> List[Dict]:
        """Get all conversations for a user"""
        try:
            response = self.supabase.table("conversations").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"[DatabaseService] Error getting conversations: {e}")
            return []
    
    def create_conversation(self, user_id: str) -> Optional[int]:
        """Create a new conversation and return its ID"""
        try:
            response = self.supabase.table("conversations").insert({"user_id": user_id}).execute()
            if response.data:
                return response.data[0].get("id")
            return None
        except Exception as e:
            print(f"[DatabaseService] Error creating conversation: {e}")
            return None
    
    def get_conversation_messages(self, conversation_id: int, user_id: str) -> List[Dict]:
        """Get all messages for a conversation"""
        try:
            # Verify conversation belongs to user
            conv = self.supabase.table("conversations").select("*").eq("id", conversation_id).eq("user_id", user_id).execute()
            if not conv.data:
                return []
            
            response = self.supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", desc=False).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"[DatabaseService] Error getting messages: {e}")
            return []
    
    def add_message(self, conversation_id: int, role: str, content: str) -> bool:
        """Add a message to a conversation"""
        try:
            entry = {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
            }
            self.supabase.table("messages").insert(entry).execute()
            return True
        except Exception as e:
            print(f"[DatabaseService] Error adding message: {e}")
            return False
    
    def get_latest_conversation(self, user_id: str) -> Optional[Dict]:
        """Get the latest conversation for a user"""
        try:
            response = self.supabase.table("conversations").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"[DatabaseService] Error getting latest conversation: {e}")
            return None

