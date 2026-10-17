# =========================================
# DOCUMENT SPLITTER
# =========================================

def split_documents(pages, source, chunk_size=900, overlap=150):
    """
    Split PDF pages into overlapping text chunks.

    Uses larger chunks so sections such as projects
    are less likely to be separated awkwardly.

    Args:
        pages: List of pages returned by load_pdf().
        source: Name of the original PDF.
        chunk_size: Maximum number of characters per chunk.
        overlap: Number of overlapping characters.

    Returns:
        List of chunks containing text and metadata.
    """

    chunks = []

    for page in pages:

        text = page["text"].strip()
        page_number = page["page"]

        if not text:
            continue

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:

                chunks.append({

                    "text": chunk_text,

                    "page": page_number,

                    "source": source

                })

            # Prevent infinite loops
            if end >= len(text):
                break

            start += chunk_size - overlap


    # =========================================
    # DEBUG
    # =========================================

    print(
        "\n========== SPLITTER DEBUG =========="
    )

    print(
        f"Total chunks created: {len(chunks)}"
    )

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        print(
            f"\n--- CHUNK {index} ---"
        )

        print(
            f"Page: {chunk['page']}"
        )

        print(
            f"Characters: {len(chunk['text'])}"
        )

        print(
            chunk["text"]
        )

    print(
        "\n===================================="
    )


    return chunks