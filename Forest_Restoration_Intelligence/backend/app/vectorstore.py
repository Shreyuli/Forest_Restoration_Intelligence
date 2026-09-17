"""RAG retrieval layer: a lightweight TF-IDF vector index over the seed corpus.

Implemented with plain Python + numpy rather than a hosted/compiled vector-DB
service, so the core reasoning pipeline stays dependency-light, fully
offline and deterministic (important for CI and for a judge running the demo
cold, without a C compiler or network access for an embedding API). The
public interface (`build_index` / `query_by_tag`) is intentionally the same
shape a Chroma- or Pinecone-backed implementation would expose, so swapping
in a hosted vector DB later is a drop-in change, not a redesign.
"""
import math
import pickle
import re
from collections import Counter
from pathlib import Path
from typing import Optional

import numpy as np

from .config import STORE_DIR, TOP_K

INDEX_PATH = Path(STORE_DIR) / "vector_index.pkl"

_TOKEN_RE = re.compile(r"[a-zA-Z]+")

_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "by",
    "is", "are", "was", "were", "be", "been", "being", "this", "that", "these",
    "those", "as", "at", "from", "it", "its", "into", "than", "then", "which",
    "their", "also", "has", "have", "had", "can", "could", "may", "might",
    "will", "would", "not", "no", "but", "if",
}


def _tokenize(text: str) -> list[str]:
    return [
        t.lower()
        for t in _TOKEN_RE.findall(text)
        if t.lower() not in _STOPWORDS and len(t) > 2
    ]


class _Index:
    def __init__(self):
        self.vocab: dict[str, int] = {}
        self.idf: np.ndarray = np.zeros(0)
        self.vectors: np.ndarray = np.zeros((0, 0))
        self.chunk_ids: list[str] = []
        self.source_ids: list[str] = []
        self.texts: list[str] = []
        self.tags: list[str] = []

    def save(self, path: Path) -> None:
        with open(path, "wb") as f:
            pickle.dump(self.__dict__, f)

    @classmethod
    def load(cls, path: Path) -> "_Index":
        idx = cls()
        with open(path, "rb") as f:
            idx.__dict__.update(pickle.load(f))
        return idx


_index: Optional[_Index] = None


def _get_index() -> _Index:
    global _index
    if _index is None:
        _index = _Index.load(INDEX_PATH)
    return _index


def _vectorize(tokens_list: list[list[str]], vocab: dict[str, int], idf: np.ndarray) -> np.ndarray:
    vectors = np.zeros((len(tokens_list), len(vocab)))
    for i, tokens in enumerate(tokens_list):
        counts = Counter(tokens)
        if not counts:
            continue
        max_count = max(counts.values())
        for term, count in counts.items():
            j = vocab.get(term)
            if j is None:
                continue
            tf = count / max_count
            vectors[i, j] = tf * idf[j]
    return vectors


def build_index(chunks: list[dict]) -> int:
    """Rebuild the vector index from scratch. chunks: list of
    {chunk_id, source_id, text, chain_link_tag}. Returns the number indexed."""
    tokens_list = [_tokenize(c["text"]) for c in chunks]

    doc_freq: Counter = Counter()
    for tokens in tokens_list:
        for term in set(tokens):
            doc_freq[term] += 1

    vocab = {term: i for i, term in enumerate(sorted(doc_freq))}
    n_docs = len(chunks)
    idf = np.zeros(len(vocab))
    for term, i in vocab.items():
        idf[i] = math.log((1 + n_docs) / (1 + doc_freq[term])) + 1.0

    vectors = _vectorize(tokens_list, vocab, idf)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    vectors = vectors / norms

    idx = _Index()
    idx.vocab = vocab
    idx.idf = idf
    idx.vectors = vectors
    idx.chunk_ids = [c["chunk_id"] for c in chunks]
    idx.source_ids = [c["source_id"] for c in chunks]
    idx.texts = [c["text"] for c in chunks]
    idx.tags = [c["chain_link_tag"] for c in chunks]
    idx.save(INDEX_PATH)

    global _index
    _index = idx
    return len(chunks)


def query_by_tag(tag: str, query_text: str = "", top_k: int = TOP_K) -> list[dict]:
    """Retrieve top-k chunks whose chain_link_tag matches `tag`, ranked by
    TF-IDF cosine similarity to `query_text` (defaults to the tag itself)."""
    idx = _get_index()
    candidate_positions = [i for i, t in enumerate(idx.tags) if t == tag]
    if not candidate_positions:
        return []

    query_text = query_text or tag.replace("_", " ").replace("->", " to ")
    tokens = _tokenize(query_text)
    q_vec = _vectorize([tokens], idx.vocab, idx.idf)[0]
    q_norm = np.linalg.norm(q_vec)
    if q_norm > 0:
        q_vec = q_vec / q_norm

    scored = [(float(np.dot(idx.vectors[pos], q_vec)), pos) for pos in candidate_positions]
    scored.sort(key=lambda x: x[0], reverse=True)

    hits = []
    for score, pos in scored[:top_k]:
        hits.append(
            {
                "chunk_id": idx.chunk_ids[pos],
                "text": idx.texts[pos],
                "source_id": idx.source_ids[pos],
                "chain_link_tag": idx.tags[pos],
                "score": score,
            }
        )
    return hits
