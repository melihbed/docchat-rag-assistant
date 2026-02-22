# 🤖 DocChat — RAG Personal Assistant

A full-stack **Retrieval-Augmented Generation (RAG)** application that lets you have intelligent conversations with your own documents (PDF/DOCX). Upload a file, ask questions in natural language, and get accurate, context-aware answers powered by OpenAI — with source citations included.

![DocChat UI](ui.png)

---

## ✨ Features

- 📄 **Document Upload** — Supports PDF and DOCX files
- 🔍 **Semantic Search** — Finds the most relevant document chunks using vector similarity
- 🧠 **RAG Pipeline** — Grounds LLM responses in your actual document content
- 💬 **Conversational Interface** — Clean chat UI built with React + Vite
- 📌 **Source Citations** — Every answer links back to the source chunks used
- 🗄️ **Vector Store** — Persistent embeddings via ChromaDB + LangChain
- 🔡 **Word Embeddings** — GloVe/Gensim integration for semantic understanding

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | Python (FastAPI) |
| LLM | OpenAI API (GPT) |
| Vector Store | ChromaDB + LangChain |
| Embeddings | OpenAI Embeddings + Gensim (GloVe) |
| Document Parsing | LangChain document loaders |
| Database | PostgreSQL |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL
- OpenAI API Key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/rag-personal-assistant.git
cd rag-personal-assistant

# Backend setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd web
npm install
```

### Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/ragdb
```

### Running the App

```bash
# Start the backend API (from root)
python main.py

# Start the frontend (in a separate terminal)
cd web
npm run dev
```

The app will be available at `http://localhost:3004`.

---

## 📐 Architecture

```
User Upload (PDF/DOCX)
        │
        ▼
  Document Loader (LangChain)
        │
        ▼
  Text Chunking (26 chunks)
        │
        ▼
  OpenAI Embeddings
        │
        ▼
  ChromaDB Vector Store ──────────────────┐
                                          │
  User Query ──► Embed Query ──► Similarity Search
                                          │
                                          ▼
                              Top-K Relevant Chunks
                                          │
                                          ▼
                              Build Prompt + Context
                                          │
                                          ▼
                                  OpenAI GPT API
                                          │
                                          ▼
                              Answer + Source Citations
```

---

## 📂 Project Structure

```
rag-personal-assistant/
├── api/                    # FastAPI backend
│   └── main.py             # API routes (/upload, /query)
├── web/                    # React frontend
│   └── src/
│       └── App.jsx         # Main chat interface
├── chroma_langchain_db/    # Persistent vector store
├── main.py                 # Application entry point
├── rag_agent.py            # RAG orchestration logic
├── rag_gensim.py           # Gensim/GloVe word embeddings
├── semantic_search.py      # Semantic search utilities
└── pyproject.toml          # Dependencies
```

---

## 💡 How It Works

1. **Upload** a PDF or DOCX document via the UI
2. The backend **parses and chunks** the document into segments
3. Each chunk is **embedded** using OpenAI's embedding model and stored in ChromaDB
4. When you ask a question, it's **embedded** and compared against stored vectors
5. The **top matching chunks** are retrieved and injected into the LLM prompt
6. OpenAI generates an answer **grounded in your document**, with source references returned to the UI

---

## 🔮 Future Improvements

- [ ] Multi-document support and cross-document queries
- [ ] Streaming responses for real-time output
- [ ] User authentication and personal document vaults
- [ ] Support for more file formats (Excel, PowerPoint, TXT)
- [ ] Hybrid search (semantic + keyword BM25)

---

## 📝 License

MIT License — feel free to use, modify, and distribute.

---

> Built with ❤️ using LangChain, ChromaDB, OpenAI, and React.
