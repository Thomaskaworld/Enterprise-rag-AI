from pypdf import PdfReader


def load_pdf(file_path):
    """
    Extract text from a PDF file.

    Args:
        file_path (str): Path to the PDF.

    Returns:
        list: Extracted text with page numbers.
    """

    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages):
        text = page.extract_text()

        if text and text.strip():
            pages.append({
                "text": text,
                "page": page_number + 1
            })

    return pages