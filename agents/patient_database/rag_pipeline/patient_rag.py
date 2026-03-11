import os
import pickle
import faiss
import numpy as np
import requests
from typing import List, Dict
import re

VECTOR_DB_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "vectordb")
VECTOR_DB_DIR = os.path.abspath(VECTOR_DB_DIR)

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
OLLAMA_EMBED_MODEL = "nomic-embed-text"


# Embedding
def embed_query(text: str) -> List[float]:
    """Embed a single text string via Ollama API."""
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={
            "model": OLLAMA_EMBED_MODEL,
            "prompt": text
        }
    )

    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()

    if "embedding" not in data:
        raise Exception(f"Invalid embedding response: {data}")

    return data["embedding"]


# Load Patient Index
def load_patient_index(patient_id: str):
    index_path = os.path.join(VECTOR_DB_DIR, f"{patient_id}.index")
    metadata_path = os.path.join(VECTOR_DB_DIR, f"{patient_id}.pkl")

    if not os.path.exists(index_path):
        raise FileNotFoundError(f"No medical records index found for patient: {patient_id}")

    index = faiss.read_index(index_path)

    with open(metadata_path, "rb") as f:
        documents = pickle.load(f)

    return index, documents


# Core Retrieval
def extract_year(query: str):
    match = re.search(r"(19|20)\d{2}", query)
    return match.group(0) if match else None


def retrieve_patient_context(patient_id: str, query: str, top_k: int = 3) -> Dict:
    """
    Retrieve relevant medical records for a patient using FAISS semantic search.

    FIX: Previously re-embedded ALL documents on every query (N HTTP calls).
    Now uses index.reconstruct_n() to extract pre-computed vectors directly
    from the FAISS .index file — only the query is embedded (1 HTTP call).
    No migration or format changes needed.
    """
    index, documents = load_patient_index(patient_id)

    # ✅ Embed only the query — 1 HTTP call regardless of number of docs
    query_vec = np.array([embed_query(query)]).astype("float32")
    faiss.normalize_L2(query_vec)

    year = extract_year(query)

    if year:
        # Get indices of documents matching the requested year
        year_indices = [
            i for i, doc in enumerate(documents)
            if doc["metadata"].get("year") == year
        ]

        if year_indices:
            # ✅ Reconstruct pre-computed vectors from .index file (no re-embed!)
            # IndexFlatIP stores raw vectors — reconstruct_n() retrieves them directly.
            all_vecs = index.reconstruct_n(0, index.ntotal)  # shape: (N, dim)
            sub_vecs = np.array([all_vecs[i] for i in year_indices]).astype("float32")
            # Vectors from build phase are already L2-normalized — no need to normalize again

            temp_index = faiss.IndexFlatIP(sub_vecs.shape[1])
            temp_index.add(sub_vecs)

            scores, sub_ids = temp_index.search(query_vec, min(top_k, len(year_indices)))
            retrieved_docs = [
                documents[year_indices[i]] for i in sub_ids[0]
                if i < len(year_indices)
            ]
        else:
            # Fallback: no documents match the year → search entire index
            scores, ids = index.search(query_vec, top_k)
            retrieved_docs = [documents[i] for i in ids[0] if i < len(documents)]
    else:
        # No year filter → search the pre-built index directly
        scores, ids = index.search(query_vec, top_k)
        retrieved_docs = [documents[i] for i in ids[0] if i < len(documents)]

    context_text = "\n\n".join([doc["text"] for doc in retrieved_docs])

    return {
        "context": context_text,
        "sources": retrieved_docs
    }

