import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from Backend.rag.loader import load_pdf
from Backend.rag.splitter import split_documents
from Backend.rag.embeddings import create_embeddings
from Backend.rag.vectorstore import add_documents
from Backend.rag.retriever import search_documents


PDF_PATH = PROJECT_ROOT / "data" / "Documents" / "ADITYA RESUME.pdf"


# Load PDF
pages = load_pdf(str(PDF_PATH))

# Create chunks
chunks = split_documents(
    pages,
    source="ADITYA RESUME.pdf"
)

# Create embeddings
texts = [chunk["text"] for chunk in chunks]

embeddings = create_embeddings(texts)

# Store chunks
add_documents(chunks, embeddings)


# Ask a question
query = "What programming languages does Aditya know?"

results = search_documents(
    query,
    top_k=3
)


print("\nQUESTION:")
print(query)

print("\nRETRIEVED RESULTS:")

for index, result in enumerate(results, start=1):
    print(f"\n--- RESULT {index} ---")
    print("Source:", result["source"])
    print("Page:", result["page"])
    print("Text:")
    print(result["text"])