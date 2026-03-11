"""
Unit tests for RAG Re-embedding Fix
Tests verify that embed_query() is called ONLY ONCE per retrieve call (for the query),
not N times (once per document). Uses mocked FAISS index and Ollama API.
"""
import sys
import os
import pickle
import tempfile
import numpy as np
import pytest
from unittest.mock import patch, MagicMock, call

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import faiss

# ─────────────────────────────────────────────────────────────────────────────
# Helpers to create a fake patient index on disk
# ─────────────────────────────────────────────────────────────────────────────

EMBED_DIM = 32  # Small dimension for tests


def make_fake_documents(n: int, year: str = "2020"):
    """Return a list of fake document dicts."""
    return [
        {
            "encounter_id": f"enc-{i}",
            "text": f"Patient visit {i} in {year}",
            "metadata": {
                "patient_id": "TestPatient",
                "year": year,
                "encounter_id": f"enc-{i}",
                "resource_type": "Encounter",
            },
        }
        for i in range(n)
    ]


def build_fake_index_on_disk(tmp_dir: str, patient_id: str, documents: list) -> str:
    """Build a real FAISS IndexFlatIP from random vectors and save to tmp_dir."""
    n = len(documents)
    vectors = np.random.rand(n, EMBED_DIM).astype("float32")
    faiss.normalize_L2(vectors)

    index = faiss.IndexFlatIP(EMBED_DIM)
    index.add(vectors)

    index_path = os.path.join(tmp_dir, f"{patient_id}.index")
    meta_path = os.path.join(tmp_dir, f"{patient_id}.pkl")

    faiss.write_index(index, index_path)
    with open(meta_path, "wb") as f:
        pickle.dump(documents, f)

    return tmp_dir


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestEmbedCallCount:
    """Core test: embed_query must be called exactly once per retrieval."""

    def test_no_year_filter_calls_embed_once(self, tmp_path):
        """Without year in query, should search pre-built index with 1 embed call."""
        pid = "TestPatient"
        docs = make_fake_documents(10, year="2020")
        build_fake_index_on_disk(str(tmp_path), pid, docs)

        fake_vec = np.random.rand(EMBED_DIM).tolist()

        import agents.patient_database.rag_pipeline.patient_rag as rag_module

        with patch.object(rag_module, "VECTOR_DB_DIR", str(tmp_path)), \
             patch.object(rag_module, "embed_query", return_value=fake_vec) as mock_embed:

            result = rag_module.retrieve_patient_context(pid, "What are my medications?", top_k=3)

        # ✅ Key assertion: embed_query called ONLY FOR THE QUERY, not documents
        assert mock_embed.call_count == 1, (
            f"embed_query called {mock_embed.call_count} times! "
            f"Expected 1 (query only). Bug: docs are being re-embedded."
        )
        assert "context" in result
        assert "sources" in result

    def test_year_filter_calls_embed_once(self, tmp_path):
        """With year in query, filter via reconstruct_n — still only 1 embed call."""
        pid = "TestPatient"
        docs = make_fake_documents(20, year="2010")
        build_fake_index_on_disk(str(tmp_path), pid, docs)

        fake_vec = np.random.rand(EMBED_DIM).tolist()

        import agents.patient_database.rag_pipeline.patient_rag as rag_module

        with patch.object(rag_module, "VECTOR_DB_DIR", str(tmp_path)), \
             patch.object(rag_module, "embed_query", return_value=fake_vec) as mock_embed:

            result = rag_module.retrieve_patient_context(
                pid, "What was my blood pressure in 2010?", top_k=3
            )

        assert mock_embed.call_count == 1, (
            f"embed_query called {mock_embed.call_count} times with year filter! "
            f"Expected 1 (query only). Bug: docs are being re-embedded."
        )
        assert len(result["sources"]) <= 3

    def test_mixed_years_year_filter_isolates_correctly(self, tmp_path):
        """Documents from 2 different years: year filter should only return matching year."""
        pid = "TestPatient"
        docs_2010 = make_fake_documents(5, year="2010")
        docs_2020 = make_fake_documents(5, year="2020")
        docs = docs_2010 + docs_2020
        build_fake_index_on_disk(str(tmp_path), pid, docs)

        fake_vec = np.random.rand(EMBED_DIM).tolist()

        import agents.patient_database.rag_pipeline.patient_rag as rag_module

        with patch.object(rag_module, "VECTOR_DB_DIR", str(tmp_path)), \
             patch.object(rag_module, "embed_query", return_value=fake_vec):

            result = rag_module.retrieve_patient_context(
                pid, "What happened in 2010?", top_k=3
            )

        # All returned sources should be from 2010
        for source in result["sources"]:
            assert source["metadata"]["year"] == "2010", (
                f"Expected year 2010 but got {source['metadata']['year']}"
            )

    def test_year_no_match_falls_back_to_full_index(self, tmp_path):
        """If year in query doesn't match any doc, should fall back to full index search."""
        pid = "TestPatient"
        docs = make_fake_documents(5, year="2020")
        build_fake_index_on_disk(str(tmp_path), pid, docs)

        fake_vec = np.random.rand(EMBED_DIM).tolist()

        import agents.patient_database.rag_pipeline.patient_rag as rag_module

        with patch.object(rag_module, "VECTOR_DB_DIR", str(tmp_path)), \
             patch.object(rag_module, "embed_query", return_value=fake_vec) as mock_embed:

            # 1999 doesn't exist in any doc
            result = rag_module.retrieve_patient_context(
                pid, "What happened in 1999?", top_k=3
            )

        # Should still return results (from full index fallback), still 1 embed call
        assert mock_embed.call_count == 1
        assert len(result["sources"]) > 0

    def test_top_k_respected(self, tmp_path):
        """Retrieved docs should not exceed top_k."""
        pid = "TestPatient"
        docs = make_fake_documents(20, year="2015")
        build_fake_index_on_disk(str(tmp_path), pid, docs)

        fake_vec = np.random.rand(EMBED_DIM).tolist()

        import agents.patient_database.rag_pipeline.patient_rag as rag_module

        with patch.object(rag_module, "VECTOR_DB_DIR", str(tmp_path)), \
             patch.object(rag_module, "embed_query", return_value=fake_vec):

            result = rag_module.retrieve_patient_context(pid, "any query", top_k=2)

        assert len(result["sources"]) <= 2


class TestLoadIndex:
    """Test load_patient_index error handling."""

    def test_missing_index_raises_file_not_found(self, tmp_path):
        """Should raise FileNotFoundError with clear message for unknown patient."""
        import agents.patient_database.rag_pipeline.patient_rag as rag_module

        with patch.object(rag_module, "VECTOR_DB_DIR", str(tmp_path)):
            with pytest.raises(FileNotFoundError, match="NoSuchPatient"):
                rag_module.load_patient_index("NoSuchPatient")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
