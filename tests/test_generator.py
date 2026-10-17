import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from Backend.rag.loader import load_pdf
from Backend.rag.splitter import split_documents
from Backend.rag.embeddings import create_embeddings
from Backend.rag.vectorstore import add_documents
from Backend.rag.retriever import search_documents
from Backend.rag.generator import generate_answer


PDF_PATH = PROJECT_ROOT / "data" / "Documents" / "ADITYA RESUME.pdf"


# 1. Load PDF
pages = load_pdf(str(PDF_PATH))

# 2. Split PDF into chunks
chunks = split_documents(
    pages,
    source="ADITYA RESUME.pdf"
)

# 3. Create embeddings
texts = [chunk["text"] for chunk in chunks]

embeddings = create_embeddings(texts)

# 4. Store chunks and embeddings in ChromaDB
add_documents(chunks, embeddings)

# 5. Ask a question
query = "What programming languages does Aditya know?"

# 6. Retrieve relevant chunks
retrieved_chunks = search_documents(
    query,
    top_k=3
)

# 7. Generate the final answer using the LLM
answer = generate_answer(
    query,
    retrieved_chunks
)

print("\nQUESTION:")
print(query)

print("\nANSWER:")
print(answer)

print("\nSOURCES:")

for chunk in retrieved_chunks:
    print(
        f"- {chunk['source']} | Page {chunk['page']}"
    )