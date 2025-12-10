# Quick Start Guide

## 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Or with a virtual environment (recommended):
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## 2. Set Up Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_BOOKS_API_KEY=your-google-books-key-here
```

**Note**: 
- OpenAI API key is **required** for the `/recommend` endpoint
- Google Books API key is optional but recommended (higher rate limits)
- OpenLibrary doesn't require an API key

## 3. Start the Backend Server

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

## 4. Test the API

### Test `/search` endpoint:
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "science fiction", "limit": 5}'
```

### Test `/recommend` endpoint:
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "books like Dune", "limit": 5}'
```

### Test health check:
```bash
curl http://localhost:8000/health
```

## 5. Start the Frontend

In a separate terminal, from the project root:

```bash
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173` and will automatically connect to the backend.

## Troubleshooting

### "OPENAI_API_KEY not found"
- Make sure you created a `.env` file in the `backend` directory
- Check that the `.env` file contains `OPENAI_API_KEY=...`

### "Connection refused" in frontend
- Make sure the backend is running on port 8000
- Check that CORS is enabled (it should be by default)
- Verify the backend URL in `src/SearchPage.jsx` matches your backend URL

### No results from APIs
- Check your internet connection
- Verify API keys are correct
- Check backend logs for error messages
- Some queries may legitimately return no results

### Embedding errors
- Verify your OpenAI API key is valid and has credits
- Check that you're using `text-embedding-3-small` model (default)
- Ensure your OpenAI account has access to embeddings API





