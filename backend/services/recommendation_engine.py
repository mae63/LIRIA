"""
Recommendation Engine
Uses embeddings and cosine similarity to rank books by relevance to user query.
"""

import numpy as np
from typing import List
from models.book import Book
from services.book_search import search_books_from_apis
from services.embedding_service import EmbeddingService


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two vectors"""
    vec1_array = np.array(vec1)
    vec2_array = np.array(vec2)
    
    dot_product = np.dot(vec1_array, vec2_array)
    norm1 = np.linalg.norm(vec1_array)
    norm2 = np.linalg.norm(vec2_array)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


class RecommendationEngine:
    """Engine for generating book recommendations using semantic similarity"""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
    
    async def get_recommendations(self, query: str, limit: int = 5) -> List[Book]:
        """
        Get book recommendations based on semantic similarity to the query.
        
        Steps:
        1. Fetch books from APIs
        2. Generate embedding for user query
        3. Generate embeddings for all book descriptions
        4. Compute cosine similarity between query and each book
        5. Rank by similarity and return top results
        """
        if not query or not query.strip():
            return []
        
        # Step 1: Fetch books (fetch more than limit to have options after filtering)
        books = await search_books_from_apis(query, limit * 3)
        
        if not books:
            return []
        
        # Step 2: Generate query embedding
        try:
            query_embedding = self.embedding_service.get_embedding(query)
        except Exception as e:
            # If embedding fails, return books without ranking
            return books[:limit]
        
        # Step 3: Generate embeddings for all book descriptions
        descriptions = [book.description for book in books]
        
        try:
            book_embeddings = self.embedding_service.get_embeddings_batch(descriptions)
        except Exception as e:
            # If batch embedding fails, return books without ranking
            return books[:limit]
        
        # Step 4: Compute similarity scores
        scored_books = []
        for i, book in enumerate(books):
            if i < len(book_embeddings):
                similarity = cosine_similarity(query_embedding, book_embeddings[i])
                book.similarity_score = similarity
                scored_books.append(book)
            else:
                # Fallback if embedding count doesn't match
                book.similarity_score = 0.0
                scored_books.append(book)
        
        # Step 5: Sort by similarity (descending) and return top results
        scored_books.sort(key=lambda b: b.similarity_score or 0.0, reverse=True)
        
        return scored_books[:limit]












