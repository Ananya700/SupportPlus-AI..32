# SupportPlus AI API

SupportPlus AI is a smart, personalized customer support backend application built with FastAPI. It acts as an advanced knowledge assistant capable of answering customer queries by combining internal company knowledge, live web search, and personalized memory to provide accurate and context-aware responses.

## 🚀 Features

- **Personalized Memory**: Uses Mem0 (backed by Qdrant) to remember user preferences, specific issues, and tailored solutions. The system actively learns from each interaction.
- **Internal Knowledge Base (RAG)**: Uses ChromaDB to store and retrieve company policies, FAQs, and internal documents.
- **Live Web Search**: Uses the Firecrawl API as a fallback to search the web for external troubleshooting steps if internal FAQs are insufficient.
- **Smart Orchestration**: Leverages LangChain and local LLMs (via Ollama) to synthesize context and deliver concise, natural responses.
- **Intelligent Caching**: Automatically caches answers to frequently asked questions to reduce LLM overhead and improve response times.

## 🛠 Tech Stack

- **Backend Framework**: FastAPI
- **LLM & Embeddings**: Ollama (Llama 3 / Nomic Embeddings)
- **AI Framework**: LangChain
- **Vector Databases**: ChromaDB (RAG) & Qdrant (Mem0)
- **Memory Engine**: Mem0
- **Web Search**: Firecrawl API

## 📋 Prerequisites

Before running the project, make sure you have the following installed and set up:
1. **Python 3.10+**
2. **Ollama**: Install [Ollama](https://ollama.com/) and ensure it is running in the background. You'll need to pull the necessary models:
   ```bash
   ollama run llama3
   ollama pull nomic-embed-text
   ```
3. **Firecrawl API Key**: Get an API key from [Firecrawl](https://firecrawl.dev/).

## ⚙️ Setup & Installation

1. **Clone the repository (if applicable)**
   ```bash
   git clone <YOUR_GITHUB_REPO_URL>
   cd "gen ai project"
   ```

2. **Create a virtual environment and activate it**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # .\venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory based on the `.env.example` file:
   ```env
   # .env
   PORT=8000
   OLLAMA_BASE_URL="http://localhost:11434"
   OLLAMA_LLM_MODEL="llama3"
   OLLAMA_EMBED_MODEL="nomic-embed-text"
   FIRECRAWL_API_KEY="your_firecrawl_api_key_here"
   ```

## 🚀 Running the Application

Start the FastAPI development server:
```bash
python main.py
# or use uvicorn directly
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will be accessible at: `http://localhost:8000`.
You can access the auto-generated API documentation at `http://localhost:8000/docs`.

## 📡 Core API Endpoints

### 1. Ask a Question
`POST /api/support/ask`

**Request Body:**
```json
{
  "user_id": "user_123",
  "session_id": "session_abc",
  "query": "How do I reset my password?"
}
```

**Description**: The primary endpoint. Synthesizes memory, internal FAQs, and web context to provide an answer. It also passively learns from the query in the background to build user memory.

### 2. Provide Feedback / Preferred Solution
`POST /api/support/feedback`

**Request Body:**
```json
{
  "user_id": "user_123",
  "issue": "Password reset email not arriving",
  "preferred_solution": "Check the spam folder and ensure the IT whitelist is active."
}
```

**Description**: Explicitly stores a preferred solution for a specific user issue in the Mem0 database so the system remembers it for future interactions.

## 🗂 Project Structure
- `main.py`: Entry point for the FastAPI server.
- `core/config.py`: Configuration and environment variable management.
- `routers/support.py`: API route definitions.
- `services/llm_service.py`: Central LLM orchestration and prompt generation.
- `services/memory_service.py`: Mem0 integration for user personalization.
- `services/rag_service.py`: Internal FAQ retrieval using ChromaDB.
- `services/firecrawl_service.py`: Web search fallback using Firecrawl.
- `services/cache_service.py`: In-memory caching for query optimization.
- `data/faqs.json`: Source file for internal company FAQs.
- `static/`: Frontend web application files.
