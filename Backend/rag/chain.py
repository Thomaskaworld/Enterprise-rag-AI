
from Backend.rag.retriever import search_documents
from Backend.rag.generator import generate_answer


FOLLOW_UP_PHRASES = (
    "tell me more",
    "more about it",
    "more about that",
    "explain it",
    "explain that",
    "what about it",
    "what about that",
    "why is that",
    "how about it",
    "elaborate",
    "continue",
    "go deeper",
    "the first one",
    "the second one",
    "the third one",
    "that project",
    "this project",
    "that person",
    "their skills",
    "his skills",
    "her skills",
    "what else",
)


def build_retrieval_query(query, chat_history=None):
    """
    Build a focused query for retrieval.

    Keeps standalone questions unchanged and adds limited context
    for follow-up questions so retrieval can find relevant chunks.
    """
    query = (query or "").strip()

    if not query or not chat_history:
        return query

    recent_history = chat_history[-6:]

    is_follow_up = (
        len(query.split()) <= 8
        or any(
            phrase in query.lower()
            for phrase in FOLLOW_UP_PHRASES
        )
    )

    if not is_follow_up:
        return query

    # Use recent user questions and assistant answers as context.
    # Limit the amount of history to avoid polluting retrieval.
    context_lines = []

    for message in recent_history:
        if not isinstance(message, dict):
            continue

        role = message.get("role", "")
        content = str(message.get("content", "")).strip()

        if role not in ("user", "assistant") or not content:
            continue

        # Keep history compact.
        content = content[:500]
        context_lines.append(f"{role}: {content}")

    if not context_lines:
        return query

    context = "\n".join(context_lines[-4:])

    return (
        f"Conversation context:\n{context}\n\n"
        f"Current question: {query}"
    )


def ask_question(query, top_k=10, chat_history=None):
    """
    Conversational RAG pipeline:
    Question -> Context-aware retrieval -> Answer -> Sources
    """
    query = (query or "").strip()

    if not query:
        return {
            "answer": "Please enter a question.",
            "sources": [],
        }

    if chat_history is None:
        chat_history = []

    retrieval_query = build_retrieval_query(
        query,
        chat_history,
    )

    retrieved_chunks = search_documents(
        retrieval_query,
        top_k=top_k,
    )

    answer = generate_answer(
        query,
        retrieved_chunks,
        chat_history=chat_history,
    )

    sources = []
    seen = set()

    for chunk in retrieved_chunks:
        source = chunk.get("source")
        page = chunk.get("page")

        if source is None or page is None:
            continue

        source_key = (source, page)

        if source_key in seen:
            continue

        sources.append({
            "document": source,
            "page": page,
        })

        seen.add(source_key)

    return {
        "answer": answer,
        "sources": sources,
    }
