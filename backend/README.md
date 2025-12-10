# LIRIA Recommendation Backend

FastAPI backend for intelligent book recommendations using OpenAI embeddings and semantic similarity search.

## Features

- **Dynamic API Integration**: Queries Google Books and OpenLibrary APIs on each request
- **Semantic Search**: Uses OpenAI embeddings (text-embedding-3-small) for intelligent matching
- **Smart Filtering**: Filters out books without meaningful descriptions or titles
- **Deduplication**: Removes duplicates based on title + author combination
- **Similarity Ranking**: Ranks books by cosine similarity to user query
- **Robust Error Handling**: Handles API timeouts, empty results, and external failures gracefully

## Setup

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys:
   # OPENAI_API_KEY=your_key_here
   # GOOGLE_BOOKS_API_KEY=your_key_here (optional, but recommended)
   # LLM_PROVIDER=gemini|mistral|openai          # default: mistral (auto gemini if GEMINI_API_KEY set)
   # LLM_API_KEY=your_mistral_or_openai_key      # for mistral/openai-compatible
   # LLM_BASE_URL=https://api.mistral.ai/v1      # default for mistral
   # LLM_MODEL=mistral-7b-instruct               # default for mistral
   # GEMINI_API_KEY=your_gemini_key              # to use Gemini (chat + embeddings if you set EMBEDDING_PROVIDER=gemini)
   # GEMINI_MODEL=gemini-1.5-flash-latest        # default for Gemini chat
   # GEMINI_EMBEDDING_MODEL=embedding-001        # default for Gemini embeddings
   # GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
   # EMBEDDING_PROVIDER=openai|gemini            # default: openai
   ```

3. **Run the server**:
   ```bash
   python main.py
   # Or with uvicorn directly:
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### `POST /search`
Search for books across both APIs without semantic ranking.

**Request**:
```json
{
  "query": "science fiction space opera",
  "limit": 10
}
```

**Response**:
```json
[
  {
    "id": "google:abc123",
    "title": "Dune",
    "author": "Frank Herbert",
    "description": "...",
    "categories": ["Science Fiction", "Fantasy"],
    "thumbnail": "https://...",
    "source": "Google Books"
  }
]
```

### `POST /recommend`
Get intelligent recommendations ranked by semantic similarity.

**Request**:
```json
{
  "query": "books similar to Dune",
  "limit": 5
}
```

**Response**:
```json
[
  {
    "id": "google:xyz789",
    "title": "Foundation",
    "author": "Isaac Asimov",
    "description": "...",
    "categories": ["Science Fiction"],
    "thumbnail": "https://...",
    "source": "Google Books",
    "similarity_score": 0.87
  }
]
```

### `GET /health`
Health check endpoint.

## Architecture

- `main.py`: FastAPI app and route handlers
- `services/book_search.py`: API clients and normalization logic
- `services/embedding_service.py`: OpenAI embedding generation
- `services/recommendation_engine.py`: Similarity ranking engine
- `models/book.py`: Pydantic models for data validation

## Error Handling

The backend handles:
- API timeouts (10s per request)
- Empty or invalid responses
- Missing API keys
- Embedding generation failures
- Network errors

All errors return appropriate HTTP status codes with descriptive messages.

