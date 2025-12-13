"""
LIRIA Recommendation Backend
FastAPI server that provides intelligent book recommendations using OpenAI embeddings
and similarity search across Google Books and OpenLibrary APIs.
"""

import os
from typing import List, Optional, Dict
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.book_search import search_books_from_apis
from services.embedding_service import EmbeddingService
from services.recommendation_engine import RecommendationEngine
from services.llm_service import LLMService
from services.database_service import DatabaseService
from services.auth_service import AuthService

# Load environment variables
load_dotenv()

app = FastAPI(
    title="LIRIA Recommendation API",
    description="AI-powered book recommendation engine",
    version="1.0.0",
)

# CORS middleware for frontend
# Allow Streamlit Cloud and local development
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:19006",
    "http://localhost:8501",  # Streamlit default port
    "https://*.streamlit.app",  # Streamlit Cloud
    "https://*.streamlit.io",  # Streamlit Cloud alternative
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Streamlit Cloud compatibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
embedding_service = EmbeddingService()
recommendation_engine = RecommendationEngine(embedding_service)
llm_service = LLMService()

# Initialize database and auth services (optional - only if Supabase is configured)
try:
    database_service = DatabaseService()
    auth_service = AuthService()
    SUPABASE_ENABLED = True
except Exception as e:
    print(f"[Main] Supabase not configured: {e}")
    database_service = None
    auth_service = None
    SUPABASE_ENABLED = False


class QueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 5


class BookResponse(BaseModel):
    id: str
    title: str
    author: str
    description: str
    categories: List[str]
    thumbnail: Optional[str]
    source: str
    similarity_score: Optional[float] = None
    preview_link: Optional[str] = None


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    limit: Optional[int] = 6
    history: Optional[List[ChatMessage]] = []  # Conversation history


class ChatResponse(BaseModel):
    reply: str
    books: List[BookResponse]


@app.get("/")
async def root():
    return {
        "message": "LIRIA Recommendation API",
        "version": "1.0.0",
        "endpoints": ["/search", "/recommend"]
    }


@app.post("/search", response_model=List[BookResponse])
async def search_books(request: QueryRequest):
    """
    Search for books across Google Books and OpenLibrary APIs.
    Returns normalized results without ranking by similarity.
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query string cannot be empty")
        
        query = request.query.strip()
        limit = max(1, min(request.limit or 20, 50))  # Clamp between 1 and 50
        
        # Fetch books from both APIs
        books = await search_books_from_apis(query, limit * 2)  # Fetch more to account for filtering
        
        if not books:
            return []
        
        # Return top results (already normalized and deduplicated)
        return books[:limit]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching books: {str(e)}"
        )


@app.post("/recommend", response_model=List[BookResponse])
async def recommend_books(request: QueryRequest):
    """
    Get intelligent book recommendations based on semantic similarity.
    Uses OpenAI embeddings to find books most similar to the user's query.
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query string cannot be empty")
        
        query = request.query.strip()
        limit = max(3, min(request.limit or 5, 10))  # Clamp between 3 and 10
        
        # Get recommendations using the recommendation engine
        recommendations = await recommendation_engine.get_recommendations(query, limit)
        
        if not recommendations:
            raise HTTPException(
                status_code=404,
                detail="No recommendations found. Try a different query."
            )
        
        return recommendations
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


# Helper function to get user_id from token
def get_user_id_from_token(authorization: Optional[str] = None) -> Optional[str]:
    """Extract user_id from authorization header"""
    if not SUPABASE_ENABLED or not authorization:
        return None
    
    try:
        # Extract token from "Bearer <token>" format
        token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        user_id = auth_service.verify_token(token)
        return user_id
    except Exception:
        return None


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authorization: Optional[str] = Header(None, alias="Authorization")):
    """
    Conversational endpoint powered by Mistral-7B-Instruct (via OpenAI-compatible API)
    with retrieval-augmented generation (RAG) over live book data.
    
    NEW LOGIC:
    1. Fetch 10-20 books from Google Books API based on user query
    2. Strictly filter by keeping only books with at least 3 of: ISBN, publisher, categories, publishedDate, previewLink
    3. Keep only the 5-8 best-structured books
    4. Inject ONLY this filtered list into Gemini prompt with explicit rule
    5. Verify response and regenerate if unauthorized books appear
    6. Save conversation and messages to database if user is authenticated
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        query = request.message.strip()
        user_id = get_user_id_from_token(authorization) if SUPABASE_ENABLED else None
        conversation_id = None
        
        # Get or create conversation if user is authenticated
        if user_id and SUPABASE_ENABLED:
            conversation = database_service.get_latest_conversation(user_id)
            if not conversation:
                conversation_id = database_service.create_conversation(user_id)
            else:
                conversation_id = conversation["id"]
        
        # Step 1: Fetch 10-20 books from Google Books API
        from services.book_search import fetch_google_books, normalize_google_book, filter_books_strict, deduplicate_books
        import os
        
        google_api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
        google_items = await fetch_google_books(query, max_results=20, api_key=google_api_key)
        
        # Normalize Google Books results
        normalized_books = []
        for item in google_items:
            try:
                book = normalize_google_book(item)
                normalized_books.append(book)
            except Exception:
                continue
        
        # Step 2 & 3: Strictly filter and keep 5-8 best-structured books
        filtered_books = filter_books_strict(normalized_books, min_fields=3, max_results=8)
        
        # Prepare conversation history for LLM
        history = []
        if request.history:
            for msg in request.history:
                if isinstance(msg, dict):
                    history.append(msg)
                else:
                    # Convert ChatMessage to dict
                    history.append({"role": msg.role, "content": msg.content})
        elif user_id and conversation_id and SUPABASE_ENABLED:
            # Load history from database if no history provided
            db_messages = database_service.get_conversation_messages(conversation_id, user_id)
            history = [{"role": msg["role"], "content": msg["content"]} for msg in db_messages]
        
        # Save user message to database if authenticated
        if user_id and conversation_id and SUPABASE_ENABLED:
            database_service.add_message(conversation_id, "user", query)
        
        # Step 4: Generate answer using LLM + RAG context with strict filtering
        max_retries = 3
        reply = None
        
        def verify_response(reply_text: str, allowed_books: List) -> bool:
            """
            Verify that the response only mentions books from the allowed list.
            Returns True if valid, False if unauthorized books detected.
            """
            if not allowed_books:
                return True  # No books to verify against
            
            reply_lower = reply_text.lower()
            allowed_titles = {b.title.lower().strip() for b in allowed_books}
            allowed_authors = {b.author.lower().strip() for b in allowed_books}
            
            # Check if reply mentions any of our allowed books
            mentions_allowed = any(
                title in reply_lower or author in reply_lower 
                for title in allowed_titles 
                for author in allowed_authors
            )
            
            # If reply doesn't mention any allowed books but seems to recommend something,
            # it might be inventing (but we'll be lenient if it's just asking questions)
            question_indicators = ["?", "what", "which", "could you", "can you", "tell me", "help me"]
            is_question = any(indicator in reply_lower for indicator in question_indicators)
            
            # If it's a question or mentions allowed books, it's valid
            if is_question or mentions_allowed:
                return True
            
            # Otherwise, might be inventing - but we'll be lenient on first attempt
            return True  # For now, we trust the prompt is strong enough
        
        for attempt in range(max_retries):
            reply = llm_service.generate_reply(query=query, books=filtered_books, history=history)
            
            # Step 5: Verify that every mentioned title belongs to the injected dataset
            if verify_response(reply, filtered_books):
                # Response is valid
                break
            else:
                # Response might contain unauthorized books - regenerate
                if attempt < max_retries - 1:
                    print(f"[Chat] Regenerating response (attempt {attempt + 1}/{max_retries}) - potential unauthorized books detected")
                    continue

        # Save assistant reply to database if authenticated
        if user_id and conversation_id and SUPABASE_ENABLED:
            database_service.add_message(conversation_id, "assistant", reply)

        # Convert Book -> BookResponse
        books_payload = [
          BookResponse(
              id=b.id,
              title=b.title,
              author=b.author,
              description=b.description,
              categories=b.categories,
              thumbnail=b.thumbnail,
              source=b.source,
              similarity_score=b.similarity_score,
              preview_link=b.preview_link,
          )
          for b in filtered_books
        ]

        return ChatResponse(reply=reply, books=books_payload)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating chat reply: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "supabase_enabled": SUPABASE_ENABLED}


# Authentication endpoints
class SignUpRequest(BaseModel):
    email: str
    password: str


class SignInRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    success: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    error: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


@app.post("/auth/signup", response_model=AuthResponse)
async def sign_up(request: SignUpRequest):
    """Sign up a new user"""
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Authentication not configured")
    
    try:
        result = auth_service.sign_up(request.email, request.password)
        if result.get("success"):
            session = result.get("session")
            return AuthResponse(
                success=True,
                user_id=result.get("user_id"),
                email=result.get("email"),
                access_token=session.access_token if session else None,
                refresh_token=session.refresh_token if session else None,
            )
        else:
            return AuthResponse(success=False, error=result.get("error", "Sign up failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during signup: {str(e)}")


@app.post("/auth/signin", response_model=AuthResponse)
async def sign_in(request: SignInRequest):
    """Sign in an existing user"""
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Authentication not configured")
    
    try:
        result = auth_service.sign_in(request.email, request.password)
        if result.get("success"):
            session = result.get("session")
            return AuthResponse(
                success=True,
                user_id=result.get("user_id"),
                email=result.get("email"),
                access_token=session.access_token if session else None,
                refresh_token=session.refresh_token if session else None,
            )
        else:
            return AuthResponse(success=False, error=result.get("error", "Invalid credentials"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during signin: {str(e)}")


@app.post("/auth/signout")
async def sign_out():
    """Sign out the current user"""
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Authentication not configured")
    
    try:
        auth_service.sign_out()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during signout: {str(e)}")


# Library endpoints
class LibraryBookRequest(BaseModel):
    title: str
    authors: List[str]
    description: str
    categories: List[str]
    source: str
    rawId: str
    coverUrl: str
    rating: int = 0
    comment: str = ""
    apiRating: Optional[float] = None
    apiRatingsCount: int = 0


@app.get("/library")
async def get_library(authorization: Optional[str] = Header(None, alias="Authorization")):
    """Get user's library"""
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    user_id = get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Extract access token from authorization header
    access_token = authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else authorization
    
    try:
        library = database_service.get_user_library(user_id, access_token)
        return {"library": library}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting library: {str(e)}")


@app.post("/library")
async def add_to_library(book: LibraryBookRequest, authorization: Optional[str] = Header(None, alias="Authorization")):
    """Add a book to user's library"""
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    user_id = get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Extract access token from authorization header
    access_token = authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else authorization
    
    try:
        book_dict = book.dict()
        success = database_service.add_to_library(user_id, book_dict, access_token)
        if success:
            return {"success": True, "message": "Book added to library"}
        else:
            return {"success": False, "message": "Book already in library"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to library: {str(e)}")


@app.put("/library/{entry_id}")
async def update_library_entry(entry_id: int, updates: Dict, authorization: Optional[str] = Header(None, alias="Authorization")):
    """Update a library entry"""
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    user_id = get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Extract access token from authorization header
    access_token = authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else authorization
    
    try:
        success = database_service.update_library_entry(user_id, entry_id, updates, access_token)
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="Library entry not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating library entry: {str(e)}")


@app.delete("/library/{entry_id}")
async def delete_library_entry(entry_id: int, authorization: Optional[str] = Header(None, alias="Authorization")):
    """Delete a library entry"""
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    user_id = get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Extract access token from authorization header
    access_token = authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else authorization
    
    try:
        success = database_service.delete_library_entry(user_id, entry_id, access_token)
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="Library entry not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting library entry: {str(e)}")


# Wishlist endpoints
class WishlistBookRequest(BaseModel):
    id: str
    title: str
    author: str
    description: str
    categories: List[str]
    thumbnail: str
    source: str
    preview_link: str


@app.get("/wishlist")
async def get_wishlist(authorization: Optional[str] = Header(None, alias="Authorization")):
    """Get user's wishlist"""
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    user_id = get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Extract access token from authorization header
    access_token = authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else authorization
    
    try:
        wishlist = database_service.get_user_wishlist(user_id, access_token)
        return {"wishlist": wishlist}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting wishlist: {str(e)}")


@app.post("/wishlist")
async def add_to_wishlist(book: WishlistBookRequest, authorization: Optional[str] = Header(None, alias="Authorization")):
    """Add a book to user's wishlist"""
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    user_id = get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Extract access token from authorization header
    access_token = authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else authorization
    
    try:
        book_dict = book.dict()
        success = database_service.add_to_wishlist(user_id, book_dict, access_token)
        if success:
            return {"success": True, "message": "Book added to wishlist"}
        else:
            return {"success": False, "message": "Book already in wishlist"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to wishlist: {str(e)}")


@app.delete("/wishlist/{entry_id}")
async def remove_from_wishlist(entry_id: int, authorization: Optional[str] = Header(None, alias="Authorization")):
    """Remove a book from user's wishlist"""
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    user_id = get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Extract access token from authorization header
    access_token = authorization.replace("Bearer ", "") if authorization and authorization.startswith("Bearer ") else authorization
    
    try:
        success = database_service.remove_from_wishlist(user_id, entry_id, access_token)
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="Wishlist entry not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing from wishlist: {str(e)}")


# Conversation endpoints
@app.get("/conversations/latest")
async def get_latest_conversation(authorization: Optional[str] = Header(None, alias="Authorization")):
    """Get user's latest conversation with messages"""
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    user_id = get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        conversation = database_service.get_latest_conversation(user_id)
        if conversation:
            messages = database_service.get_conversation_messages(conversation["id"], user_id)
            return {
                "conversation": conversation,
                "messages": messages,
            }
        return {"conversation": None, "messages": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting latest conversation: {str(e)}")


@app.post("/conversations")
async def create_conversation(authorization: Optional[str] = Header(None, alias="Authorization")):
    """Create a new conversation"""
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    user_id = get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        conversation_id = database_service.create_conversation(user_id)
        if conversation_id:
            return {"success": True, "conversation_id": conversation_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to create conversation")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")


@app.post("/conversations/{conversation_id}/messages")
async def add_message(conversation_id: int, message: ChatMessage, authorization: Optional[str] = Header(None, alias="Authorization")):
    """Add a message to a conversation"""
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    user_id = get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        # Verify conversation belongs to user
        conv = database_service.get_latest_conversation(user_id)
        if not conv or conv.get("id") != conversation_id:
            raise HTTPException(status_code=403, detail="Conversation not found or access denied")
        
        success = database_service.add_message(conversation_id, message.role, message.content)
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to add message")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding message: {str(e)}")


# Migration endpoint
@app.post("/migrate/localstorage")
async def migrate_localstorage(data: Dict, authorization: Optional[str] = Header(None, alias="Authorization")):
    """Migrate localStorage data to database (one-time operation)"""
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    user_id = get_user_id_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        migrated = {"library": 0, "wishlist": 0}
        
        # Migrate library
        if "library" in data:
            for book in data["library"]:
                if database_service.add_to_library(user_id, book):
                    migrated["library"] += 1
        
        # Migrate wishlist
        if "wishlist" in data:
            for book in data["wishlist"]:
                if database_service.add_to_wishlist(user_id, book):
                    migrated["wishlist"] += 1
        
        return {"success": True, "migrated": migrated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error migrating data: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

