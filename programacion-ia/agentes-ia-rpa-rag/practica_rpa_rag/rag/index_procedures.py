"""Indexa los workflows JSON de procedures/ en ChromaDB.
Uso: python rag/index_procedures.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

ROOT = Path(__file__).resolve().parent.parent
PROCEDURES_DIR = ROOT / "procedures"
CHROMA_DIR = ROOT / "rag" / ".chroma"
COLLECTION_NAME = "procedures"

sys.path.insert(0, str(ROOT))


_EMBEDDINGS: HuggingFaceEmbeddings | None = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Embeddings locales con sentence-transformers, cacheados a nivel de
    módulo (cargar el modelo cuesta varios segundos)."""
    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        _EMBEDDINGS = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            encode_kwargs={"normalize_embeddings": True},
        )
    return _EMBEDDINGS


def workflow_to_document(wf: dict, source: str) -> Document:
    """Workflow JSON -> Document (solo título + descripción + tags)."""
    tags = ", ".join(wf.get("tags", []))

    text = (
        f"Título: {wf['titulo']}\n"
        f"Descripción: {wf['descripcion']}\n"
        f"Tags: {tags}"
    )

    metadata = {
        "id": wf["id"],
        "titulo": wf["titulo"],
        "app": wf.get("app", ""),
        "source": source,
    }
    return Document(page_content=text, metadata=metadata)


def load_workflows() -> List[Document]:
    """Lee los workflows con shared.procedures y los pasa a Documents."""
    if not PROCEDURES_DIR.exists():
        raise FileNotFoundError(f"No existe {PROCEDURES_DIR}")

    # Diferido: shared/procedures.py necesita ROOT en sys.path.
    from shared.procedures import iter_workflows

    docs: List[Document] = []
    for wf in iter_workflows():
        # source es solo metadato.
        source = str(PROCEDURES_DIR / f"{wf['id']}.workflow.json")
        docs.append(workflow_to_document(wf, source=source))
        print(f"  - {wf['id']}.workflow.json  ->  id={wf['id']}")
    return docs


def main() -> None:
    print("Cargando workflows de procedures/ ...")
    docs = load_workflows()
    if not docs:
        print("No se encontraron *.workflow.json en procedures/")
        sys.exit(1)

    print(f"Generando embeddings (total: {len(docs)} workflows) ...")
    embeddings = get_embeddings()

    # Recreo la colección para no acumular duplicados al reindexar.
    if CHROMA_DIR.exists():
        import shutil
        shutil.rmtree(CHROMA_DIR)

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Persistiendo en ChromaDB -> {CHROMA_DIR}")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
    )

    # Chroma 0.4+ persiste solo; llamada por retrocompatibilidad.
    if hasattr(vectorstore, "persist"):
        try:
            vectorstore.persist()
        except Exception:
            pass

    print(f"Indexación completada ({len(docs)} documento(s)).")


if __name__ == "__main__":
    main()
