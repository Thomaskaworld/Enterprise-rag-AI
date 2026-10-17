from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import shutil
from pathlib import Path


from Backend.rag.chain import ask_question
from Backend.rag.loader import load_pdf
from Backend.rag.splitter import split_documents
from Backend.rag.embeddings import create_embeddings

from Backend.rag.vectorstore import (
    add_documents,
    get_documents as get_vector_documents,
    delete_document as delete_vector_document
)


# =========================================
# APPLICATION
# =========================================

app = FastAPI(
    title="Enterprise RAG AI",
    description="AI-powered document question answering system",
    version="1.0.0"
)


# =========================================
# CORS
# =========================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================
# REQUEST MODELS
# =========================================

class QuestionRequest(BaseModel):

    question: str


# =========================================
# CHAT HISTORY
# =========================================

chat_history = []


# =========================================
# ROOT
# =========================================

@app.get("/")
def root():

    return {
        "message": "Enterprise RAG AI is running!"
    }


# =========================================
# ASK QUESTION
# =========================================

@app.post("/ask")
def ask(request: QuestionRequest):

    global chat_history

    # -----------------------------------------
    # Get current question
    # -----------------------------------------

    question = request.question.strip()


    # -----------------------------------------
    # Ask RAG pipeline
    # -----------------------------------------

    result = ask_question(
        question,
        chat_history=chat_history
    )


    # -----------------------------------------
    # Save user message
    # -----------------------------------------

    chat_history.append({

        "role": "user",

        "content": question

    })


    # -----------------------------------------
    # Save AI response
    # -----------------------------------------

    chat_history.append({

        "role": "assistant",

        "content": result["answer"]

    })


    # -----------------------------------------
    # Keep only recent conversation
    # -----------------------------------------

    if len(chat_history) > 10:

        chat_history = chat_history[-10:]


    # -----------------------------------------
    # Return response
    # -----------------------------------------

    return {

        "question":
            question,

        "answer":
            result["answer"],

        "sources":
            result["sources"]

    }
# =========================================
# CLEAR CHAT
# =========================================

@app.post("/clear-chat")
def clear_chat():

    global chat_history

    chat_history = []

    return {

        "success": True,

        "message":
            "Conversation cleared successfully."

    }


# =========================================
# UPLOAD PDF
# =========================================

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    # -----------------------------------------
    # Check file type
    # -----------------------------------------

    if not file.filename.lower().endswith(".pdf"):

        return {

            "success": False,

            "message":
                "Only PDF files are supported."

        }


    # -----------------------------------------
    # Create directory
    # -----------------------------------------

    upload_directory = Path(
        "data/Documents"
    )

    upload_directory.mkdir(
        parents=True,
        exist_ok=True
    )


    # -----------------------------------------
    # PDF path
    # -----------------------------------------

    pdf_path = (
        upload_directory /
        file.filename
    )


    # -----------------------------------------
    # If same document already exists
    # remove old vectors first
    # -----------------------------------------

    try:

        delete_vector_document(
            file.filename
        )

    except Exception as error:

        print(
            "Old vector deletion skipped:",
            error
        )


    # -----------------------------------------
    # Save PDF
    # -----------------------------------------

    with open(
        pdf_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    # -----------------------------------------
    # Load PDF
    # -----------------------------------------

    pages = load_pdf(
        str(pdf_path)
    )


    # -----------------------------------------
    # Split PDF
    # -----------------------------------------

    chunks = split_documents(
        pages,

        source=file.filename
    )


    # -----------------------------------------
    # Extract text
    # -----------------------------------------

    texts = [

        chunk["text"]

        for chunk in chunks

    ]


    # -----------------------------------------
    # Create embeddings
    # -----------------------------------------

    embeddings = create_embeddings(
        texts
    )


    # -----------------------------------------
    # Store in ChromaDB
    # -----------------------------------------

    stored_chunks = add_documents(
        chunks,
        embeddings
    )


    # -----------------------------------------
    # Response
    # -----------------------------------------

    return {

        "success": True,

        "message":
            "PDF uploaded and indexed successfully.",

        "filename":
            file.filename,

        "pages":
            len(pages),

        "chunks":
            stored_chunks

    }


# =========================================
# LIST DOCUMENTS
# =========================================

@app.get("/documents")
def list_documents():

    try:

        documents = get_vector_documents()

        return {

            "documents":
                documents,

            "count":
                len(documents)

        }

    except Exception as error:

        print(
            "Error loading documents:",
            error
        )

        return {

            "documents": [],

            "count": 0,

            "error":
                str(error)

        }


# =========================================
# DELETE DOCUMENT
# =========================================

@app.delete("/documents/{filename}")
def delete_document(filename: str):

    # -----------------------------------------
    # Delete from ChromaDB
    # -----------------------------------------

    try:

        delete_vector_document(
            filename
        )

    except Exception as error:

        print(
            "ChromaDB deletion error:",
            error
        )


    # -----------------------------------------
    # Delete physical PDF
    # -----------------------------------------

    pdf_path = (
        Path("data/Documents") /
        filename
    )


    if pdf_path.exists():

        pdf_path.unlink()


    return {

        "success": True,

        "message":
            f"{filename} deleted successfully."

    }