# Author: Maharshi Soni | License: MIT
"""Bridge wrapping embedkit for semantic search as MCP tools.

Attempts to import embedkit for embedding-based search; falls back to
TF-IDF based search if the package is not installed.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

# Graceful fallback: try embedkit, fall back to TF-IDF
try:
    from embedkit import EmbedKit  # type: ignore[import-untyped]
    _HAS_EMBEDKIT = True
except ImportError:
    _HAS_EMBEDKIT = False


def semantic_search_impl(query: str, documents_dir: str) -> str:
    """Search documents using semantic similarity.

    Uses embedkit when available, otherwise falls back to TF-IDF search.

    Args:
        query: Natural language search query.
        documents_dir: Path to a directory containing documents to search.

    Returns:
        JSON string with ranked search results.
    """
    if not query or not query.strip():
        return json.dumps({"error": "Query is required"})

    doc_path = Path(documents_dir)
    if not doc_path.exists():
        return json.dumps({"error": f"Directory does not exist: {documents_dir}"})

    documents = _load_documents(doc_path)
    if not documents:
        return json.dumps({"error": "No searchable documents found in directory"})

    if _HAS_EMBEDKIT:
        return _search_with_embedkit(query, documents)

    return _search_with_tfidf(query, documents)


def get_knowledge_base_info(documents_dir: str = ".") -> str:
    """Return metadata about available indexed documents.

    Args:
        documents_dir: Path to the documents directory.

    Returns:
        JSON string with knowledge base summary.
    """
    doc_path = Path(documents_dir)
    if not doc_path.exists():
        return json.dumps({"error": f"Directory does not exist: {documents_dir}"})

    documents = _load_documents(doc_path)
    file_types: dict[str, int] = {}
    total_size = 0

    for doc in documents:
        ext = doc["extension"]
        file_types[ext] = file_types.get(ext, 0) + 1
        total_size += doc["size"]

    return json.dumps(
        {
            "documents_dir": documents_dir,
            "total_documents": len(documents),
            "total_size_bytes": total_size,
            "file_types": file_types,
            "engine": "embedkit" if _HAS_EMBEDKIT else "tfidf_fallback",
            "indexed_files": [
                {"name": d["name"], "extension": d["extension"], "size": d["size"]}
                for d in documents[:50]
            ],
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Document Loading
# ---------------------------------------------------------------------------


_SEARCHABLE_EXTENSIONS = {".py", ".txt", ".md", ".rst", ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini"}


def _load_documents(directory: Path) -> list[dict[str, Any]]:
    """Load all searchable documents from a directory."""
    documents: list[dict[str, Any]] = []

    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in _SEARCHABLE_EXTENSIONS:
            continue
        if any(part.startswith(".") for part in file_path.parts):
            continue
        if "__pycache__" in str(file_path):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue

        if not content.strip():
            continue

        documents.append({
            "name": file_path.name,
            "path": str(file_path),
            "relative_path": str(file_path.relative_to(directory)),
            "extension": file_path.suffix.lower(),
            "content": content,
            "size": len(content),
        })

    return documents


# ---------------------------------------------------------------------------
# EmbedKit Search
# ---------------------------------------------------------------------------


def _search_with_embedkit(query: str, documents: list[dict[str, Any]]) -> str:
    """Search using embedkit embeddings."""
    try:
        kit = EmbedKit()  # type: ignore[name-defined]
        texts = [d["content"][:2000] for d in documents]
        results = kit.search(query, texts, top_k=10)  # type: ignore[attr-defined]

        ranked = []
        for idx, score in results:
            doc = documents[idx]
            ranked.append({
                "file": doc["relative_path"],
                "score": round(float(score), 4),
                "snippet": doc["content"][:300].strip(),
            })

        return json.dumps(
            {
                "query": query,
                "engine": "embedkit",
                "total_documents": len(documents),
                "results_count": len(ranked),
                "results": ranked,
            },
            indent=2,
        )
    except Exception as exc:
        return _search_with_tfidf(query, documents)


# ---------------------------------------------------------------------------
# TF-IDF Fallback
# ---------------------------------------------------------------------------


def _search_with_tfidf(query: str, documents: list[dict[str, Any]]) -> str:
    """Search using TF-IDF similarity (no external dependencies)."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return json.dumps({"error": "Query produced no searchable tokens"})

    # Build document frequency
    doc_freq: Counter[str] = Counter()
    doc_tokens: list[list[str]] = []
    for doc in documents:
        tokens = _tokenize(doc["content"])
        doc_tokens.append(tokens)
        unique = set(tokens)
        for token in unique:
            doc_freq[token] += 1

    n_docs = len(documents)
    scored: list[tuple[int, float]] = []

    for i, tokens in enumerate(doc_tokens):
        if not tokens:
            continue
        tf = Counter(tokens)
        score = 0.0
        for qt in query_tokens:
            if qt in tf:
                term_freq = tf[qt] / len(tokens)
                idf = math.log((n_docs + 1) / (doc_freq.get(qt, 0) + 1)) + 1
                score += term_freq * idf
        if score > 0:
            scored.append((i, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    top_results = scored[:10]

    results = []
    for idx, score in top_results:
        doc = documents[idx]
        snippet = _extract_snippet(doc["content"], query_tokens)
        results.append({
            "file": doc["relative_path"],
            "score": round(score, 4),
            "snippet": snippet,
        })

    return json.dumps(
        {
            "query": query,
            "engine": "tfidf_fallback",
            "total_documents": len(documents),
            "results_count": len(results),
            "results": results,
        },
        indent=2,
    )


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer with lowercasing."""
    return [
        token
        for token in re.findall(r"[a-z0-9_]+", text.lower())
        if len(token) > 1
    ]


def _extract_snippet(content: str, query_tokens: list[str], max_len: int = 300) -> str:
    """Extract the most relevant snippet containing query terms."""
    content_lower = content.lower()
    best_pos = 0
    best_score = 0

    for qt in query_tokens:
        pos = content_lower.find(qt)
        if pos >= 0:
            # Score by proximity to start + number of query terms nearby
            window = content_lower[max(0, pos - 100):pos + 200]
            score = sum(1 for t in query_tokens if t in window)
            if score > best_score:
                best_score = score
                best_pos = max(0, pos - 50)

    snippet = content[best_pos:best_pos + max_len].strip()
    if best_pos > 0:
        snippet = "..." + snippet
    if best_pos + max_len < len(content):
        snippet = snippet + "..."

    return snippet
