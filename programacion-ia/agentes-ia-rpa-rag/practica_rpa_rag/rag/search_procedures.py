"""Búsqueda semántica sobre los workflows indexados en ChromaDB.
Uso: python rag/search_procedures.py "tu consulta"
"""
from __future__ import annotations

import sys
from pathlib import Path

from langchain_chroma import Chroma

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from rag.index_procedures import CHROMA_DIR, COLLECTION_NAME, get_embeddings  # noqa: E402
from shared.procedures import load_workflow  # noqa: E402


# Cacheo a nivel de módulo: cargar el modelo y abrir Chroma cuesta segundos.
_VECTORSTORE: Chroma | None = None


def _open_vectorstore() -> Chroma:
    global _VECTORSTORE
    if _VECTORSTORE is None:
        _VECTORSTORE = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=str(CHROMA_DIR),
            embedding_function=get_embeddings(),
        )
    return _VECTORSTORE


def search(query: str, k: int = 3) -> list[dict]:
    """Top-k workflows más similares a `query` con score normalizado en [0,1]."""
    vs = _open_vectorstore()
    results = vs.similarity_search_with_relevance_scores(query, k=k)
    out: list[dict] = []
    for doc, score in results:
        out.append({
            "id": doc.metadata.get("id"),
            "titulo": doc.metadata.get("titulo"),
            "score": round(float(score), 4),
            "snippet": doc.page_content,
        })
    return out


def search_procedure(query: str, min_score: float = 0.2) -> dict | None:
    """Mejor workflow y su contenido completo. None si ninguno alcanza min_score."""
    hits = search(query, k=1)
    if not hits:
        return None
    best = hits[0]
    if best["score"] < min_score:
        return None
    wf = load_workflow(best["id"])
    if wf is None:
        return None
    return {"id": best["id"], "score": best["score"], "workflow": wf}


def main() -> None:
    if len(sys.argv) < 2:
        print('Uso: python rag/search_procedures.py "tu consulta"')
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    print(f"Buscando: {query!r}")
    hits = search(query, k=3)
    if not hits:
        print("Sin resultados.")
        return
    for i, h in enumerate(hits, 1):
        print(f"\n  [{i}] id={h['id']}  score={h['score']}")
        print(f"      título: {h['titulo']}")
        print(f"      {h['snippet'].splitlines()[0]}")


if __name__ == "__main__":
    main()
