import sys
from pathlib import Path

# Add the Enterprise RAG AI project root to Python's path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from Backend.rag.loader import load_pdf
from Backend.rag.splitter import split_documents


PDF_PATH = PROJECT_ROOT / "data" / "Documents" / "ADITYA RESUME.pdf"

# Load the PDF
pages = load_pdf(str(PDF_PATH))

# Split the extracted text into chunks
chunks = split_documents(
    pages,
    source="ADITYA RESUME.pdf"
)

print("PDF pages:", len(pages))
print("Total chunks:", len(chunks))

print("\n--- FIRST CHUNK ---")
print(chunks[0])