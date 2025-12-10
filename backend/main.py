"""
LIRIA Recommendation Backend
FastAPI server that provides intelligent book recommendations using OpenAI embeddings
and similarity search across Google Books and OpenLibrary APIs.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.book_search import search_books_from_apis
from services.embedding_service import EmbeddingService
from services.recommendation_engine import RecommendationEngine
from services.llm_service import LLMService

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


class ChatRequest(BaseModel):
    message: str
    limit: Optional[int] = 6


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


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Conversational endpoint powered by Mistral-7B-Instruct (via OpenAI-compatible API)
    with retrieval-augmented generation (RAG) over live book data.
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        query = request.message.strip()
        limit = max(3, min(request.limit or 6, 10))

        # Retrieve fresh books to ground the LLM response
        books = await search_books_from_apis(query, limit * 2)
        books = books[:limit] if books else []

        # Generate answer using LLM + RAG context
        reply = llm_service.generate_reply(query=query, books=books)

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
          )
          for b in books
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
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

