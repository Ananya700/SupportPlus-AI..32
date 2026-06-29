from mem0 import Memory
from core.config import settings

class MemoryService:
    def __init__(self):
        self._config = {
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": settings.OLLAMA_LLM_MODEL
                }
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": settings.OLLAMA_EMBED_MODEL
                }
            },
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": "supportplus_memory",
                    "path": "./qdrant_data"
                }
            }
        }
        self._memory = None
        self._initialized = None  # None = not yet attempted

    def _ensure_initialized(self):
        """Lazy initialization — only runs on first actual use, avoiding
        the uvicorn reloader lock conflict."""
        if self._initialized is not None:
            return self._initialized
        try:
            self._memory = Memory.from_config(self._config)
            self._initialized = True
            print("Mem0 initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize Mem0: {e}")
            self._initialized = False
        return self._initialized

    def store_solution(self, user_id: str, issue: str, preferred_solution: str):
        """Stores a frequent issue and its preferred solution in memory."""
        if not self._ensure_initialized():
            return
            
        content = f"User '{user_id}' frequently asks about: '{issue}'. The preferred working solution is: '{preferred_solution}'"
        self._memory.add(content, user_id=user_id)

    def retrieve_memory(self, user_id: str, query: str):
        """Retrieves relevant past memories for a user based on the query."""
        if not self._ensure_initialized():
            return ""
            
        results = self._memory.search(query, filters={"user_id": user_id})
        if not results:
            return ""
            
        # Format the results
        memories = [item['memory'] for item in results if 'memory' in item]
        if not memories:
            return ""
            
        return "\n".join(memories)

    def learn_from_interaction(self, user_id: str, message: str):
        """Passively learns from a user message (intended to run in the background)."""
        if not self._ensure_initialized():
            return
            
        try:
            # Mem0 will use the LLM to automatically extract and store facts/preferences
            self._memory.add(message, user_id=user_id)
            print(f"Mem0 successfully analyzed interaction for user '{user_id}'")
        except Exception as e:
            print(f"Failed to extract memory from interaction: {e}")

memory_service = MemoryService()
