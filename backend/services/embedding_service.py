"""
Embedding Service
Supports:
- OpenAI text-embedding-3-small (default)
- Google Gemini embeddings (embedding-001)
"""

import os
from typing import List
import httpx
from openai import OpenAI


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        self.provider = os.getenv("EMBEDDING_PROVIDER", "").lower().strip()

        # OpenAI setup
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

        # Gemini setup
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_EMBEDDING_MODEL", "embedding-001")
        self.gemini_base = os.getenv(
            "GEMINI_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta",
        )

        # Auto-select provider if not specified
        if not self.provider:
            if self.gemini_api_key:
                self.provider = "gemini"
            else:
                self.provider = "openai"

        if self.provider == "gemini":
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY is required for Gemini embeddings")
        elif self.provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required for OpenAI embeddings")
            self.client = OpenAI(api_key=self.openai_api_key)
        else:
            raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {self.provider}")

    def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.openai_model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def _embed_gemini(self, texts: List[str]) -> List[List[float]]:
        # Gemini batch: call once per text (API supports one content per call)
        embeddings = []
        url = f"{self.gemini_base}/models/{self.gemini_model}:embedContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": self.gemini_api_key}

        with httpx.Client(timeout=30.0) as client:
            for text in texts:
                payload = {"content": {"parts": [{"text": text}]}}
                r = client.post(url, headers=headers, params=params, json=payload)
                r.raise_for_status()
                data = r.json()
                embedding = data.get("embedding", {}).get("value")
                if not embedding:
                    raise RuntimeError("Gemini returned no embedding value")
                embeddings.append(embedding)
        return embeddings

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts."""
        if not texts:
            return []
        valid_texts = [t.strip() for t in texts if t and t.strip()]
        if not valid_texts:
            return []

        try:
            if self.provider == "gemini":
                return self._embed_gemini(valid_texts)
            return self._embed_openai(valid_texts)
        except Exception as e:
            raise RuntimeError(f"Failed to generate embeddings: {str(e)}")

    def get_embedding(self, text: str) -> List[float]:
        """Get a single embedding by delegating to batch method."""
        embeddings = self.get_embeddings_batch([text])
        return embeddings[0] if embeddings else []



