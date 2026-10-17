import chromadb
import uuid


# =========================================
# CHROMA DATABASE
# =========================================

CHROMA_PATH = "data/chroma_db"

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_or_create_collection(
    name="enterprise_documents"
)


# =========================================
# ADD DOCUMENTS
# =========================================

def add_documents(chunks, embeddings):
    """
    Add document chunks and embeddings to ChromaDB.

    Each chunk stores:
        - text
        - source filename
        - page number

    If the same document already exists,
    its previous chunks are removed first.
    """

    if not chunks:
        return 0


    # =========================================
    # VALIDATE EMBEDDINGS
    # =========================================

    if len(chunks) != len(embeddings):

        raise ValueError(
            "Number of chunks and embeddings "
            "must be the same."
        )


    # =========================================
    # DOCUMENT NAME
    # =========================================

    filename = chunks[0]["source"]


    # =========================================
    # REMOVE OLD VERSION
    # =========================================

    try:

        collection.delete(
            where={
                "source": filename
            }
        )

    except Exception as error:

        print(
            "Warning while deleting old document:",
            error
        )


    # =========================================
    # PREPARE DATA
    # =========================================

    ids = []

    documents = []

    metadatas = []


    for index, chunk in enumerate(chunks):

        chunk_id = (
            f"{filename}_"
            f"{chunk['page']}_"
            f"{index}_"
            f"{uuid.uuid4().hex}"
        )


        ids.append(
            chunk_id
        )


        documents.append(
            chunk["text"]
        )


        metadatas.append({

            "source":
                filename,

            "page":
                chunk["page"],

            "chunk_index":
                index

        })


    # =========================================
    # STORE IN CHROMADB
    # =========================================

    collection.add(

        ids=ids,

        documents=documents,

        embeddings=embeddings.tolist(),

        metadatas=metadatas

    )


    print(
        f"Stored {len(ids)} chunks "
        f"for '{filename}'"
    )


    return len(ids)


# =========================================
# GET DOCUMENTS
# =========================================

def get_documents():
    """
    Return all unique documents currently
    stored in ChromaDB.

    Each document contains:
        filename
        pages
        chunks
    """

    results = collection.get(
        include=["metadatas"]
    )


    metadatas = results.get(
        "metadatas",
        []
    )


    documents = {}


    # =========================================
    # BUILD DOCUMENT INFORMATION
    # =========================================

    for metadata in metadatas:

        if not metadata:
            continue


        source = metadata.get(
            "source"
        )

        page = metadata.get(
            "page"
        )


        if not source:
            continue


        if source not in documents:

            documents[source] = {

                "filename":
                    source,

                "pages":
                    set(),

                "chunks":
                    0

            }


        if page is not None:

            documents[source][
                "pages"
            ].add(page)


        documents[source][
            "chunks"
        ] += 1


    # =========================================
    # FORMAT RESPONSE
    # =========================================

    document_list = []


    for document in documents.values():

        document_list.append({

            "filename":
                document["filename"],

            "pages":
                len(
                    document["pages"]
                ),

            "chunks":
                document["chunks"]

        })


    # =========================================
    # SORT DOCUMENTS
    # =========================================

    document_list.sort(

        key=lambda document:
            document["filename"].lower()

    )


    return document_list


# =========================================
# DELETE DOCUMENT
# =========================================

def delete_document(filename):
    """
    Delete all chunks belonging to a
    specific document.
    """

    collection.delete(

        where={
            "source": filename
        }

    )


    print(
        f"Deleted document: {filename}"
    )


    return True


# =========================================
# GET COLLECTION STATISTICS
# =========================================

def get_collection_stats():
    """
    Return basic ChromaDB statistics.
    """

    total_chunks = collection.count()


    documents = get_documents()


    return {

        "total_chunks":
            total_chunks,

        "total_documents":
            len(documents)

    }