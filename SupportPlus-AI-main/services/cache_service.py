import json
import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from core.config import settings

CACHE_DIR = "./chroma_cache"
SIMILARITY_THRESHOLD = 0.85  # Minimum similarity to consider a cache hit

class CacheService:
    """Caches query-response pairs using ChromaDB for semantic matching.
    When a user asks a question similar to a previously answered one,
    the cached response is returned instantly without calling the LLM."""

    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            model=settings.OLLAMA_EMBED_MODEL,
            base_url=settings.OLLAMA_BASE_URL
        )
        self._store = None
        self._initialized = False

    def _ensure_initialized(self):
        if self._initialized:
            return
        try:
            if os.path.exists(CACHE_DIR):
                self._store = Chroma(
                    collection_name="response_cache",
                    persist_directory=CACHE_DIR,
                    embedding_function=self.embeddings
                )
            else:
                self._store = Chroma(
                    collection_name="response_cache",
                    persist_directory=CACHE_DIR,
                    embedding_function=self.embeddings
                )
            self._initialized = True
            print(f"Cache service initialized. Entries: {self._store._collection.count()}")
        except Exception as e:
            print(f"Failed to initialize cache: {e}")
            self._initialized = False

    def lookup(self, query: str):
        """Check if a similar query has been answered before.
        Returns the cached response string, or None if no match."""
        self._ensure_initialized()
        if not self._store:
            return None

        try:
            results = self._store.similarity_search_with_relevance_scores(query, k=1)
            if not results:
                return None

            doc, score = results[0]
            if score >= SIMILARITY_THRESHOLD:
                cached_response = doc.metadata.get("response", "")
                original_query = doc.metadata.get("query", "")
                print(f"[Cache HIT] score={score:.3f} | original=\"{original_query[:60]}\"")
                return cached_response

            print(f"[Cache MISS] best score={score:.3f} (threshold={SIMILARITY_THRESHOLD})")
            return None
        except Exception as e:
            print(f"Cache lookup error: {e}")
            return None

    def store(self, query: str, response: str):
        """Save a query-response pair to the cache."""
        self._ensure_initialized()
        if not self._store:
            return

        try:
            doc = Document(
                page_content=query,
                metadata={
                    "query": query,
                    "response": response
                }
            )
            self._store.add_documents([doc])
            print(f"[Cache STORE] \"{query[:60]}\"")
        except Exception as e:
            print(f"Cache store error: {e}")

cache_service = CacheService()
