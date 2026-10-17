
import re

from Backend.rag.embeddings import create_embeddings
from Backend.rag.vectorstore import collection


# =========================================
# RELEVANCE THRESHOLDS
# =========================================

NORMAL_THRESHOLD = 1.80
BROAD_THRESHOLD = 1.95


# =========================================
# BROAD QUERY DETECTION
# =========================================

def is_broad_query(query):
    query_lower = (query or "").lower()

    broad_keywords = [
        "projects",
        "project",
        "experience",
        "skills",
        "skill",
        "education",
        "certifications",
        "certification",
        "technologies",
        "technology",
        "programming languages",
        "languages",
        "worked on",
        "work",
        "background",
        "profile",
        "resume",
        "cv",
    ]

    return any(
        keyword in query_lower
        for keyword in broad_keywords
    )


# =========================================
# DOCUMENT HINT DETECTION
# =========================================

def detect_document_hint(query):
    """
    Detect whether the question targets Aditya or Greeshma.

    If the query contains conversation context, prioritize
    the current question. Otherwise, use the most recent
    explicitly mentioned person in the query.
    """
    query_lower = (query or "").lower()

    # Prefer the explicitly stated person in the current question.
    current_match = re.search(
        r"current question:\s*(.*)",
        query_lower,
        re.DOTALL,
    )

    if current_match:
        current_question = current_match.group(1)

        if re.search(r"\baditya\b", current_question):
            return "aditya"

        if re.search(r"\bgreeshma\b", current_question):
            return "greeshma"

    # Inspect user messages from newest to oldest.
    user_messages = re.findall(
        r"user:\s*(.*?)(?=\n\s*(?:user|assistant):|$)",
        query_lower,
        re.DOTALL,
    )

    for message in reversed(user_messages):
        if re.search(r"\baditya\b", message):
            return "aditya"

        if re.search(r"\bgreeshma\b", message):
            return "greeshma"

    # Fallback: last explicitly mentioned person.
    matches = list(
        re.finditer(
            r"\b(aditya|greeshma)\b",
            query_lower,
        )
    )

    if matches:
        return matches[-1].group(1)

    return None


# =========================================
# DOCUMENT NAME MATCHING
# =========================================

def document_matches_hint(document_hint, source):
    """
    Ensure the selected person's query only retrieves
    chunks from their corresponding PDF.
    """
    source_lower = (
        (source or "")
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )

    print(
        f"[DOCUMENT FILTER] hint={document_hint!r}, "
        f"source={source!r}"
    )

    if not document_hint:
        return True

    if document_hint == "aditya":
        return "aditya" in source_lower

    if document_hint == "greeshma":
        return "greeshma" in source_lower

    return True


# =========================================
# SEARCH DOCUMENTS
# =========================================

def search_documents(query, top_k=10):
    """
    Retrieve relevant chunks from ChromaDB.

    Supports:
    - Semantic retrieval
    - Broad queries
    - Person-specific PDF filtering
    - Relevance thresholds
    - Source and page metadata
    """

    query = (query or "").strip()

    if not query:
        return []

    # =====================================
    # DETERMINE QUERY TYPE
    # =====================================

    broad_query = is_broad_query(query)
    document_hint = detect_document_hint(query)

    if broad_query:
        relevance_threshold = BROAD_THRESHOLD
        search_k = max(top_k, 12)
    else:
        relevance_threshold = NORMAL_THRESHOLD
        search_k = top_k

    print("\n========== RETRIEVAL DEBUG ==========")
    print(f"Query: {query}")
    print(
        f"Query type: "
        f"{'BROAD' if broad_query else 'NORMAL'}"
    )
    print(f"Document hint: {document_hint or 'NONE'}")
    print(f"Threshold: {relevance_threshold}")
    print(f"Top K: {search_k}")

    # =====================================
    # CREATE QUERY EMBEDDING
    # =====================================

    query_embedding = create_embeddings([query])[0]

    # =====================================
    # SEARCH CHROMADB
    # =====================================

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=search_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    documents_list = results.get("documents") or [[]]
    metadatas_list = results.get("metadatas") or [[]]
    distances_list = results.get("distances") or [[]]

    documents = documents_list[0] if documents_list else []
    metadatas = metadatas_list[0] if metadatas_list else []
    distances = distances_list[0] if distances_list else []

    print("\nOriginal retrieval results:")

    for index, (document, metadata, distance) in enumerate(
        zip(documents, metadatas, distances),
        start=1,
    ):
        print(
            f"{index}. Distance: {distance:.4f} | "
            f"Source: {metadata.get('source')} | "
            f"Page: {metadata.get('page')}"
        )

    # =====================================
    # FILTER RESULTS
    # =====================================

    retrieved_chunks = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        source = metadata.get("source", "Unknown")
        page = metadata.get("page", "Unknown")

        # Reject irrelevant chunks.
        if distance > relevance_threshold:
            print(
                f"Filtered out: {source} page {page} "
                f"(distance {distance:.4f} exceeds threshold)"
            )
            continue

        # Reject chunks from the wrong person's document.
        if not document_matches_hint(document_hint, source):
            print(
                f"Filtered out: {source} page {page} "
                f"(document mismatch)"
            )
            continue

        retrieved_chunks.append({
            "text": document,
            "page": page,
            "source": source,
            "distance": distance,
        })

    # =====================================
    # SORT AND LIMIT
    # =====================================

    retrieved_chunks.sort(
        key=lambda chunk: chunk["distance"]
    )

    retrieved_chunks = retrieved_chunks[:search_k]

    # =====================================
    # DEBUG OUTPUT
    # =====================================

    print(
        f"\nRelevant chunks returned: "
        f"{len(retrieved_chunks)}"
    )

    print("\n========== RETRIEVED TEXT ==========")

    if not retrieved_chunks:
        print(
            "No chunks passed the relevance "
            "or document filter."
        )

    for index, chunk in enumerate(
        retrieved_chunks,
        start=1,
    ):
        print(f"\n--- CHUNK {index} ---")
        print(f"Distance: {chunk['distance']:.4f}")
        print(f"Source: {chunk['source']}")
        print(f"Page: {chunk['page']}")
        print("Content:")
        print(chunk["text"])

    print("\n====================================")

    return retrieved_chunks
