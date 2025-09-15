import numpy as np
from query_expand import generate_query_variants
from hybrid_search import fuzzy_topk, combine_scores
from utils_normalize import normalize_fa

# کمک‌تابع: جمع‌آوری امتیاز FAISS برای یک عبارت
def _faiss_scores_for_text(model, index, text, top_k):
    q = model.encode([text], normalize_embeddings=True, convert_to_numpy=True).astype("float32")
    scores, indices = index.search(q, top_k)  # (1, k)
    out = {}
    for sc, idx in zip(scores[0], indices[0]):
        if idx >= 0:
            i = int(idx)
            s = float(sc)      # چون بردارها نرمال: IP == cosine
            if s > out.get(i, -1):
                out[i] = s
    return out  # dict: index_id -> score

def retrieve_hybrid(user_query, state=None, k_emb=40, k_fuzzy=80, k_final=10):
    # اجزا
    if state is not None:
        model = state["model"]; metadata = state["metadata"]
        index = state["index"]; bm25 = state["bm25"]; questions = state["questions"]
    else:
        # fallback (کندتر): فقط اگر STATE ندادی
        from search_similarity import load_components
        from hybrid_search import build_bm25
        model, metadata, index = load_components()
        bm25, questions, _ = build_bm25(metadata)

    # 1) واریانت‌ها
    variants = generate_query_variants(user_query)

    # 2) FAISS برای همه واریانت‌ها
    emb_scores = {}
    for v in variants:
        local = _faiss_scores_for_text(model, index, v, top_k=k_emb)
        for i, s in local.items():
            if s > emb_scores.get(i, -1):
                emb_scores[i] = s

    # 3) فازی (روی سوال‌های نرمال‌شده)
    qn = normalize_fa(user_query)
    fuzzy_list = fuzzy_topk(qn, questions, k=k_fuzzy)
    fuzzy_scores = {i: s for i, s in fuzzy_list}

    # 4) BM25
    bm25_scores = {}
    for v in variants:
        toks = v.split()
        scores = bm25.get_scores(toks)  # np.array
        if (scores.max() - scores.min()) > 0:
            norm = (scores - scores.min()) / (scores.max() - scores.min())
        else:
            norm = np.zeros_like(scores)
        for i, s in enumerate(norm):
            if s > bm25_scores.get(i, -1):
                bm25_scores[i] = float(s)

    # 5) ترکیب و انتخاب
    combo = combine_scores(emb_scores, fuzzy_scores, bm25_scores, w=(0.65, 0.25, 0.10))
    top = combo[:k_final]

    # 6) خروجی
    results = []
    for i, s in top:
        row = metadata.iloc[int(i)].to_dict() if hasattr(metadata, "iloc") else dict(metadata[int(i)])
        row["hybrid_score"] = round(float(s), 4)
        row["_index_id"] = int(i)
        results.append(row)
    return results
