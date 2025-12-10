"""
LLM Service for conversational responses.
Supports:
- mistralai/Mistral-7B-Instruct (OpenAI-compatible)
- Google Gemini (via Generative Language API)
"""

import os
from typing import List
import httpx
from openai import OpenAI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
from models.book import Book


SYSTEM_PROMPT = """You are LIRIA, a highly knowledgeable and demanding literary advisor, specialized in helping readers find the right book for the right moment.

Your role is not to list popular titles, but to identify meaningful, relevant, and well-targeted book recommendations based on the user's taste, reading history, and current desire.

You must follow these rules at all times:

1. You never invent books, authors, or titles.
   You only recommend books that are explicitly provided by the system and that are available on Google Books or OpenLibrary.
   If no books are provided, you must ask short clarifying questions before recommending anything.

2. You behave like an expert bookseller.
   You ask concise, intelligent follow-up questions, never long interviews.
   You focus only on what is essential to refine the recommendation.

3. You must propose book recommendations early in the discussion.
   Even if the request is vague, you should:
   - suggest 1–2 initial books,
   - then ask 1–2 short questions to refine the next suggestions.

4. You adapt your recommendations to the user's level.
   If the user is inexperienced, you stay accessible.
   If the user is experienced, you avoid generic or overhyped books and favor more demanding or niche works.

5. You prioritize relevance over popularity.
   You never push bestsellers unless they genuinely match the user's request.

6. When recommending a book, you must:
   - clearly name the title and the author (use EXACT titles and authors as provided, in plain text with no markdown formatting),
   - explain precisely and briefly why this book matches the request (using ONLY the description provided, never invent details),
   - avoid generic or vague justifications.

7. You are allowed to gently challenge the user's habits by suggesting adjacent literary territories, but you must always explain the connection simply.

8. Your tone must be:
   - natural,
   - cultured,
   - warm,
   - concise,
   - like a real independent bookseller.
   You are never robotic and never marketing-oriented.

9. You must never refer to yourself as an artificial intelligence, a model, or a software.
   You are simply LIRIA, a literary advisor.

10. If the user's request is impossible, unclear, or contradictory, you explain the issue calmly and guide them toward a better-defined request.

11. Your goal is not only to recommend a book, but to help the reader progress, refine their taste, and discover literature with confidence — without overwhelming them with long explanations.

TECHNICAL REQUIREMENTS:
- NEVER use markdown formatting (no **, *, __, _). Write in plain text only.
- PRIORITIZE individual novels and standalone books over collections, anthologies, or "megapacks" (only recommend collections if no individual novels match).
- Use ONLY the information provided in the book descriptions. Never invent details that aren't in the description.
"""


class LLMService:
    """Handles chat generation with RAG-augmented context."""

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "mistral").lower()

        # Mistral / OpenAI-compatible defaults
        self.llm_api_key = (
            os.getenv("LLM_API_KEY")
            or os.getenv("MISTRAL_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        self.llm_base_url = os.getenv("LLM_BASE_URL", "https://api.mistral.ai/v1")
        self.llm_model = os.getenv("LLM_MODEL", "mistral-7b-instruct")

        # Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_APIKEY")
        # Default to gemma-3-27b-it (might have better quota availability)
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemma-3-27b-it")

        # Choose provider automatically if GEMINI_API_KEY is present
        if self.gemini_api_key and self.provider not in {"mistral", "openai"}:
            self.provider = "gemini"

        # Initialize OpenAI-compatible client if needed
        if self.provider in {"mistral", "openai"}:
            if not self.llm_api_key:
                raise ValueError("LLM_API_KEY / MISTRAL_API_KEY / OPENAI_API_KEY is required")
            self.client = OpenAI(api_key=self.llm_api_key, base_url=self.llm_base_url)

        # Initialize Gemini client if needed
        if self.provider == "gemini":
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY is required for Gemini provider")
            if not GEMINI_AVAILABLE:
                raise ValueError("google-generativeai package is required. Install with: pip install google-generativeai")
            genai.configure(api_key=self.gemini_api_key)

    def _build_context_block(self, books: List[Book]) -> str:
        """Create a textual context block from retrieved books."""
        if not books:
            return "No books found."
        
        lines = []
        for i, b in enumerate(books, 1):
            # Use full description - don't truncate (LLM needs complete info to describe accurately)
            desc = b.description.strip() if b.description else "No description available."
            categories_str = ', '.join(b.categories[:3]) if b.categories else 'N/A'
            
            lines.append(
                f"{i}. {b.title} by {b.author}\n"
                f"   Categories: {categories_str}\n"
                f"   Description: {desc}\n"
            )
        return "\n".join(lines)

    def _generate_mistral(self, query: str, context_block: str) -> str:
        has_books = context_block.strip() and context_block.strip() != "No books found."
        
        if has_books:
            system_content = (
                f"=== AVAILABLE BOOKS (USE ONLY THESE - NEVER INVENT) ===\n"
                f"{context_block}\n"
                f"=== END OF AVAILABLE BOOKS ===\n\n"
                f"Remember: Work only with the books listed above. Use their exact titles and authors. Base your recommendations on the descriptions provided. Write in plain text only (no markdown)."
            )
        else:
            system_content = (
                f"=== AVAILABLE BOOKS ===\n"
                f"No books found in the search results.\n"
                f"=== END OF AVAILABLE BOOKS ===\n\n"
                f"Remember: Since no books were found, ask intelligent clarifying questions to understand the user's needs better. Do not say 'there are no books' - instead, be a helpful literary advisor gathering information. Write in plain text only (no markdown)."
            )
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": system_content},
            {"role": "user", "content": query},
        ]
        resp = self.client.chat.completions.create(
            model=self.llm_model,
            messages=messages,
            temperature=0.4,
            max_tokens=450,
        )
        return resp.choices[0].message.content.strip()

    def _generate_gemini(self, query: str, context_block: str) -> str:
        """Generate response using Google Generative AI library."""
        has_books = context_block.strip() and context_block.strip() != "No books found."
        
        if has_books:
            prompt_text = (
                SYSTEM_PROMPT
                + "\n\n=== AVAILABLE BOOKS (USE ONLY THESE - NEVER INVENT) ===\n"
                + context_block
                + "\n=== END OF AVAILABLE BOOKS ===\n\n"
                + "User query: " + query
                + "\n\nRemember: Work only with the books listed above. Use their exact titles and authors. Base your recommendations on the descriptions provided. Write in plain text only (no markdown)."
            )
        else:
            prompt_text = (
                SYSTEM_PROMPT
                + "\n\n=== AVAILABLE BOOKS ===\n"
                + "No books found in the search results.\n"
                + "=== END OF AVAILABLE BOOKS ===\n\n"
                + "User query: " + query
                + "\n\nRemember: Since no books were found, ask intelligent clarifying questions to understand the user's needs better. Do not say 'there are no books' - instead, be a helpful literary advisor gathering information. Write in plain text only (no markdown)."
            )
        
        # Try multiple models in order of preference
        # Prioritize Gemma models (might have different quotas) and Flash models
        models_to_try = []
        if self.gemini_model:
            models_to_try.append(self.gemini_model)
        # Try Gemma models first (they might have different quotas)
        models_to_try.extend([
            "gemma-3-27b-it",  # Large Gemma model
            "gemma-3-12b-it",  # Medium Gemma model
            "gemini-2.5-flash",  # Fast stable version
            "gemini-flash-latest",  # Latest flash
            "gemini-2.5-pro",  # Stable version (might have quota issues)
            "gemini-pro-latest",  # Latest release (might have quota issues)
        ])
        
        last_error = None
        quota_error_models = set()  # Track models that hit quota limits
        
        for model_name in models_to_try:
            # Skip models that already hit quota limits
            if model_name in quota_error_models:
                continue
                
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt_text,
                    generation_config={
                        "temperature": 0.4,
                        "max_output_tokens": 450,
                    },
                    safety_settings=[
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ]
                )
                
                # Check for safety blocks (finish_reason 2 = SAFETY)
                if response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'finish_reason') and candidate.finish_reason == 2:
                        # Safety filter blocked - try to get partial text or skip
                        print(f"[LLMService] Gemini model '{model_name}' blocked by safety filter")
                        continue
                
                # Try to get text from response
                try:
                    text = response.text
                    if text and text.strip():
                        return text.strip()
                except ValueError as ve:
                    # response.text might fail if finish_reason is SAFETY
                    print(f"[LLMService] Gemini model '{model_name}' text access failed: {ve}")
                    continue
                
                raise ValueError("Gemini returned empty response")
                
            except Exception as e:
                error_str = str(e)
                last_error = e
                
                # Check if it's a quota error (429)
                if "429" in error_str or "quota" in error_str.lower() or "Quota exceeded" in error_str:
                    print(f"[LLMService] Gemini model '{model_name}' quota exceeded, skipping similar models")
                    quota_error_models.add(model_name)
                    # Also skip similar models (e.g., if gemini-2.5-pro fails, skip gemini-pro-latest)
                    if "2.5-pro" in model_name:
                        quota_error_models.add("gemini-pro-latest")
                    elif "pro-latest" in model_name:
                        quota_error_models.add("gemini-2.5-pro")
                else:
                    print(f"[LLMService] Gemini model '{model_name}' failed: {e}")
                continue
        
        raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

    def _clean_markdown(self, text: str) -> str:
        """Remove markdown formatting from text."""
        import re
        # Remove bold/italic markdown (**text**, *text*, __text__, _text_)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        # Remove any remaining single asterisks or underscores used for emphasis
        text = text.replace('**', '').replace('*', '').replace('__', '').replace('_', '')
        return text.strip()

    def generate_reply(self, query: str, books: List[Book]) -> str:
        """Generate a conversational reply using the selected provider with RAG context."""
        context_block = self._build_context_block(books)

        try:
            if self.provider == "gemini":
                reply = self._generate_gemini(query, context_block)
            else:
                reply = self._generate_mistral(query, context_block)
            
            # Clean markdown from response
            return self._clean_markdown(reply)
        except Exception as e:
            # Fallback: minimal graceful response
            print(f"[LLMService] provider={self.provider} error: {e}")
            return (
                "I'm having trouble generating a response right now. "
                "Could you rephrase your request or try again in a moment?"
            )



