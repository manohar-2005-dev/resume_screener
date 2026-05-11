import logging
import chromadb
from chromadb.utils import embedding_functions
from typing import List
from config import VECTOR_STORE_PATH, EMBEDDING_MODEL

logger = logging.getLogger(__name__)


def get_embedding_function():
    """
    Load HuggingFace embedding model.
    Uses sentence-transformers/all-MiniLM-L6-v2.
    """
    # ChromaDB has built-in HuggingFace embedding support
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )


def get_vectorstore(collection_name: str = "resumes"):
    """
    Create or connect to ChromaDB collection.
    Persists to disk at VECTOR_STORE_PATH.
    """
    # YOUR TASK:
    # Step 1: create chromadb.PersistentClient(path=VECTOR_STORE_PATH)
    chromadb_client = chromadb.PersistentClient(path=VECTOR_STORE_PATH)
    # Step 2: get_embedding_function()
    embedding_function = get_embedding_function()
    # Step 3: client.get_or_create_collection(
    #             name=collection_name,
    #             embedding_function=embedding_function
    #         )
    collection = chromadb_client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )
    # Step 4: return collection
    return collection


def store_chunks(chunks: List[dict]) -> int:
    """
    Store resume chunks in ChromaDB.
    Returns number of chunks stored.
    """
    # YOUR TASK:
    # Step 1: get_vectorstore()
    collection = get_vectorstore()
    # Step 2: extract from chunks list:
    #         - ids:       [chunk["chunk_id"] for chunk in chunks]
    #         - documents: [chunk["text"] for chunk in chunks]
    #         - metadatas: [{"candidate_name": chunk["candidate_name"],
    #                        "source_file": chunk["source_file"],
    #                        "chunk_index": chunk["chunk_index"]} 
    #                       for chunk in chunks]
    ids = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [{"candidate_name": chunk["candidate_name"],
                    "source_file": chunk["source_file"],
                    "chunk_index": chunk["chunk_index"]} 
                     for chunk in chunks]
    # Step 3: collection.add(ids, documents, metadatas)
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    # Step 4: log how many chunks stored
    logger.info(f"Stored {len(chunks)} chunks in vector store.")
    # Step 5: return len(chunks)
    return len(chunks)


def search_similar(query_text: str, n_results: int = 5) -> List[dict]:
    """
    Search ChromaDB for chunks similar to query_text.
    Returns list of results with text and metadata.
    """
    # YOUR TASK:
    # Step 1: get_vectorstore()
    collection = get_vectorstore()
    # Step 2: collection.query(
    #             query_texts=[query_text],
    #             n_results=n_results
    #         )
    results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
    # Step 3: results contains "documents" and "metadatas" lists
    #         zip them together into list of dicts
    formatted_results = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        formatted_results.append({
        "text": doc,
        "candidate_name": meta.get("candidate_name", "unknown"),
        "source_file": meta.get("source_file", "unknown"),
        "chunk_index": meta.get("chunk_index", 0)
    })
    # Step 4: return formatted results
    return formatted_results


def clear_vectorstore():
    """Delete and recreate the collection. Useful for testing."""
    client = chromadb.PersistentClient(path=VECTOR_STORE_PATH)
    client.delete_collection("resumes")
    logger.info("Vector store cleared.")


if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    from src.ingestion.loader import load_resume
    from src.preprocessing.parser import parse_resume
    from src.chunking.splitter import chunk_resume

    # Load → Parse → Chunk
    loaded = load_resume("data/samples/resume_DS_Intern.pdf")
    parsed = parse_resume(loaded["raw_text"])
    parsed["file_name"] = loaded["file_name"]
    chunks = chunk_resume(parsed)

    # Store
    stored = store_chunks(chunks)
    print(f"\n✅ Stored {stored} chunks in vector database")

    # Search
    query = "Python developer with machine learning experience"
    results = search_similar(query, n_results=3)

    print(f"\n🔍 Search: '{query}'")
    print(f"Top {len(results)} results:\n")
    for i, result in enumerate(results):
        print(f"── Result {i+1} ──")
        print(f"   Candidate : {result['candidate_name']}")
        print(f"   Chunk     : {result['chunk_index']}")
        print(f"   Preview   : {result['text'][:120]}...")
        print()