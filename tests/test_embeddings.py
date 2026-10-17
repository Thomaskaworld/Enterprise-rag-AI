import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from Backend.rag.loader import load_pdf
from Backend.rag.splitter import split_documents
from Backend.rag.embeddings import create_embeddings


PDF_PATH = PROJECT_ROOT / "data" / "Documents" / "ADITYA RESUME.pdf"


# 1. Load PDF
pages = load_pdf(str(PDF_PATH))

# 2. Create chunks
chunks = split_documents(
    pages,
    source="ADITYA RESUME.pdf"
)

# 3. Extract text from chunks
texts = [chunk["text"] for chunk in chunks]

# 4. Create embeddings
embeddings = create_embeddings(texts)


print("Number of chunks:", len(chunks))
print("Number of embeddings:", len(embeddings))
print("Embedding dimensions:", len(embeddings[0]))

print("\nFirst embedding:")
print(embeddings[0][:10])