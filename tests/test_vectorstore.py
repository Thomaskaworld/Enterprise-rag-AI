import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from Backend.rag.loader import load_pdf
from Backend.rag.splitter import split_documents
from Backend.rag.embeddings import create_embeddings
from Backend.rag.vectorstore import add_documents


PDF_PATH = PROJECT_ROOT / "data" / "Documents" / "ADITYA RESUME.pdf"


# 1. Load PDF
pages = load_pdf(str(PDF_PATH))

# 2. Split into chunks
chunks = split_documents(
    pages,
    source="ADITYA RESUME.pdf"
)

# 3. Get text
texts = [chunk["text"] for chunk in chunks]

# 4. Create embeddings
embeddings = create_embeddings(texts)

# 5. Store everything in ChromaDB
count = add_documents(chunks, embeddings)

print("PDF pages:", len(pages))
print("Chunks:", len(chunks))
print("Embeddings:", len(embeddings))
print("Documents stored in ChromaDB:", count)