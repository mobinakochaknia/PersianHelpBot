import numpy as np
from rapidfuzz import fuzz, process
from rank_bm25 import BM25Okapi

def _questions_from_meta(metadata, use_norm=True):
    # سعی کن اگر question_norm وجود دارد همان را استفاده کنی
    if hasattr(metadata, "iloc"):
        col = "question_norm" if "question_norm" in metadata.columns else "question"
        return list(metadata[col].fillna("").astype(str))
    elif isinstance(metadata, (list, tuple)):
        return [dict(m).get("question","") for m in metadata]
    return []

def build_bm25(metadata, tokenizer=lambda s: s.split()):
    questions = _questions_from_meta(metadata)
    corpus = [tokenizer(q) for q in questions]
    return BM25Okapi(corpus), questions, corpus

def fuzzy_topk(query_norm, questions, k=50):
    items = process.extract(query_norm, questions, scorer=fuzz.token_set_ratio, limit=k)
    return [(idx, sc/100.0) for _, sc, idx in items]

def combine_scores(emb_scores, fuzzy_scores, bm25_scores, w=(0.65,0.25,0.10)):
    idxs = set(emb_scores) | set(fuzzy_scores) | set(bm25_scores)
    out = []
    for i in idxs:
        s = w[0]*emb_scores.get(i,0) + w[1]*fuzzy_scores.get(i,0) + w[2]*bm25_scores.get(i,0)
        out.append((i, s))
    out.sort(key=lambda x: x[1], reverse=True)
    return out
