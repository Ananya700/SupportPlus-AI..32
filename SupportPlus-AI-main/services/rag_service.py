import json
import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from core.config import settings

class RAGService:
    def __init__(self, data_path="data/faqs.json", persist_directory="./chroma_db"):
        self.data_path = data_path
        self.persist_directory = persist_directory
        
        self.embeddings = OllamaEmbeddings(
            model=settings.OLLAMA_EMBED_MODEL,
            base_url=settings.OLLAMA_BASE_URL
        )
        self.vector_store = None
        self._initialize_db()

    def _initialize_db(self):
        """Load FAQs and create vector store if it doesn't exist."""
        if not os.path.exists(self.persist_directory):
            documents = self._load_faqs()
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
        else:
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )

    def _load_faqs(self):
        """Read FAQs from JSON file and convert to Documents."""
        if not os.path.exists(self.data_path):
            return []
            
        with open(self.data_path, "r") as f:
            faqs = json.load(f)
            
        documents = []
        for faq in faqs:
            content = f"Question: {faq['question']}\nAnswer: {faq['answer']}"
            doc = Document(page_content=content, metadata={"source": "internal_faq"})
            documents.append(doc)
            
        return documents

    def search(self, query: str, k: int = 2):
        """Search for relevant FAQs."""
        if not self.vector_store:
            return "RAG Service is not initialized."
            
        results = self.vector_store.similarity_search(query, k=k)
        if not results:
            return ""
            
        context = "\n\n".join([doc.page_content for doc in results])
        return context

rag_service = RAGService()
