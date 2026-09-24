# 🧠 Mnemo

### Your AI journal that remembers

Mnemo is a private AI-powered journal application that allows users to securely store their personal journal entries and ask questions about their past memories using AI.

The application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant journal entries through semantic search and provide them as context to an LLM before generating an answer.

---

## 📖 Overview

Mnemo combines a journal application with AI-powered memory.

Users can:

- Create journal entries
- View their previous journal entries
- Ask questions about their past entries
- Retrieve relevant memories using semantic search
- Get AI-generated answers based on their own journal data

Each user's journal data is isolated using authentication and user-specific database queries.

---

## ✨ Features

- 🔐 User authentication using Supabase Auth
- 📝 Create and store journal entries
- 📚 View personal journal entries
- 🧬 Generate embeddings for journal entries
- 🔎 Semantic similarity search
- 👤 User-specific data access
- 💬 RAG-based AI question answering
- 📌 Display retrieved journal sources with AI answers
- 🔌 LLM provider abstraction
- 🖥️ Streamlit frontend
- ⚡ FastAPI backend

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python, FastAPI |
| Database | Supabase PostgreSQL |
| Vector Search | pgvector |
| Authentication | Supabase Auth |
| Embeddings | Sentence Transformers |
| Embedding Model | all-MiniLM-L6-v2 |
| LLM Integration | OpenRouter / Ollama |
| Configuration | python-dotenv |

---

## 🏗️ Project Architecture

```text
                    ┌─────────────────────┐
                    │   Streamlit Frontend│
                    └──────────┬──────────┘
                               │
                         HTTP / JSON
                               │
                    ┌──────────▼──────────┐
                    │    FastAPI Backend  │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      Authentication     Journal Storage    AI / RAG
             │                 │                 │
             ▼                 ▼                 ▼
      Supabase Auth       PostgreSQL       Embeddings
                               │                 │
                               ▼                 ▼
                           pgvector          LLM Provider
                                                 │
                                      ┌──────────┴──────────┐
                                      ▼                     ▼
                                  OpenRouter              Ollama