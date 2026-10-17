import sys
from pathlib import Path

# Find the Enterprise RAG AI project folder
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Add the project folder to Python's import path
sys.path.insert(0, str(PROJECT_ROOT))

from Backend.rag.loader import load_pdf


PDF_PATH = PROJECT_ROOT / "data" / "Documents" / "ADITYA RESUME.pdf"

pages = load_pdf(str(PDF_PATH))

print("PDF successfully loaded!")
print("Number of pages:", len(pages))

if pages:
    print("\nFirst page number:", pages[0]["page"])
    print("\nFirst page text:")
    print(pages[0]["text"][:1000])