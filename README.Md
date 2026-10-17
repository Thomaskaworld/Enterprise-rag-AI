
# Enterprise RAG AI — Document Intelligence Assistant

An AI-powered document question-answering system built with Retrieval-Augmented Generation (RAG). Upload PDF documents, ask questions in natural language, and receive answers grounded in retrieved document content with source and page references.

## Features

- PDF upload and text extraction
- Text chunking and embedding generation
- Semantic search using ChromaDB
- AI-powered answers using Groq
- Source document and page references
- Multi-document retrieval
- Person-specific document filtering
- Web interface for uploading documents and asking questions

## Tech Stack

- Python
- FastAPI
- Groq API
- ChromaDB
- Sentence Transformers
- HTML, CSS, JavaScript
- Git and GitHub

## Project Structure

```text
Enterprise RAG AI/
├── Backend/
│   ├── main.py
│   └── rag/
├── Frontend/
├── tests/
├── data/              # Local data; not committed
├── .env.example
├── .gitignore
└── README.md
```

## Prerequisites

- Python installed
- A Groq API key
- Git installed

## Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd "Enterprise RAG AI"
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bat
venv\Scripts\activate
```

### 3. Install dependencies

Install the packages listed in `requirements.txt`.

### 4. Configure environment variables

Create a `.env` file in the project root and add:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your own key. Never commit `.env`.

### 5. Start the backend

```bash
uvicorn Backend.main:app --reload
```

Backend: http://127.0.0.1:8000

### 6. Start the frontend

Open another terminal:

```bash
cd Frontend
python -m http.server 5500
```

Frontend: http://127.0.0.1:5500

## Usage

1. Start the backend and frontend.
2. Upload a PDF through the web interface.
3. Wait for the document to be indexed.
4. Ask questions about the uploaded content.
5. Review the answer and its cited sources.

## Security Notes

- Keep API keys in environment variables.
- Do not commit `.env`, private documents, or local vector database files.
- Verify `.gitignore` before pushing the repository publicly.

## Future Improvements

- Improved conversational retrieval
- Retrieval evaluation and automated tests
- Docker-based deployment
- Production hosting and monitoring

## Author

Aditya — B.Tech Computer Science Engineering, AI & ML
