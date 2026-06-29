from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from core.config import settings
from services.rag_service import rag_service
from services.firecrawl_service import firecrawl_service
from services.memory_service import memory_service
from services.cache_service import cache_service

class LLMService:
    def __init__(self):
        self.session_histories = {}
        self.llm = ChatOllama(
            model=settings.OLLAMA_LLM_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.3
        )
            
        self.prompt_template = PromptTemplate.from_template(
            """You are SupportPlus AI, a smart knowledge enhancer for customer support.
            
You have access to the following information to help answer the user's question:

1. Past User Preferences & Memories (from Mem0):
{memories}

2. Internal FAQs (from RAG):
{faqs}

3. Web Troubleshooting Steps (from Firecrawl):
{web_context}

4. Previous Conversation History:
{chat_history}

User Question: {query}

Instructions:
- Prioritize past preferences and memories if they are highly relevant to the user.
- Use Internal FAQs as the primary source of truth for company policies.
- If Internal FAQs do not provide a complete solution, use the Web Troubleshooting Steps.
- Synthesize the information into a clear, helpful, and concise response. 
- Do not mention the internal names of your tools (e.g., don't say "According to Firecrawl" or "My RAG says"). Just provide the answer naturally.

Answer:
"""
        )

    async def generate_response(self, user_id: str, session_id: str, query: str):
        if not self.llm:
            return {"answer": "LLM Service is not initialized.", "cached": False, "source": "error"}

        # Initialize session history if it doesn't exist
        if session_id not in self.session_histories:
            self.session_histories[session_id] = []

        # 0. Check cache for a similar previously answered query
        cached = cache_service.lookup(query)
        if cached:
            return {"answer": cached, "cached": True, "source": "cache"}

        # 1. Retrieve Memories
        memories = memory_service.retrieve_memory(user_id=user_id, query=query)
        
        # 2. Retrieve Internal FAQs
        faqs = rag_service.search(query=query)
        
        # 3. Assess if we need web context
        web_context = ""
        source = "rag"
        if not faqs:
            web_context = firecrawl_service.search_web(query=query)
            source = "web"
        
        if memories:
            source = "memory+" + source
            
        # 4. Generate Response
        history_list = self.session_histories[session_id]
        chat_history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history_list])
        if not chat_history_str:
            chat_history_str = "No previous conversation."

        prompt = self.prompt_template.format(
            memories=memories if memories else "None available.",
            faqs=faqs if faqs else "None available.",
            web_context=web_context if web_context else "None available.",
            chat_history=chat_history_str,
            query=query
        )
        
        try:
            response = self.llm.invoke(prompt)
            answer = response.content

            # 5. Auto-save to cache for future reuse
            cache_service.store(query, answer)

            # 6. Update session history
            self.session_histories[session_id].append({"role": "User", "content": query})
            self.session_histories[session_id].append({"role": "Assistant", "content": answer})
            # Keep only the last 10 messages (5 turns) to prevent context overflow
            if len(self.session_histories[session_id]) > 10:
                self.session_histories[session_id] = self.session_histories[session_id][-10:]

            return {"answer": answer, "cached": False, "source": source}
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return {"answer": "I'm sorry, I encountered an error while generating a response. Ensure Ollama is running.", "cached": False, "source": "error"}

llm_service = LLMService()
