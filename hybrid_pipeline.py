import numpy as np
from search_similarity import load_components, find_similar_questions
from query_expand import generate_query_variants
from hybrid_search import build_bm25, fuzzy_topk, combine_scores
from utils_normalize import normalize_fa

def retrieve_hybrid(user_query, k_emb=40, k_fuzzy=80, k_final=10):
    # لود اجزای فعلی تو
    model, metadata, index = load_components()
    bm25, questions, corpus = build_bm25(metadata)

    # 1) واریانت‌ها
    variants = generate_query_variants(user_query)

    # 2) FAISS برای همه واریانت‌ها (threshold پایین برای جمع‌آوری گسترده)
    emb_scores = {}
    for v in variants:
        hits = find_similar_questions(v, top_k=k_emb, threshold=0.0)
        for h in hits:
            i = int(h["index_id"])
            emb_scores[i] = max(emb_scores.get(i,0), float(h["similarity_score"]))

    # 3) فازی
    qn = normalize_fa(user_query)
    fuzzy_list = fuzzy_topk(qn, questions, k=k_fuzzy)
    fuzzy_scores = {i:s for i,s in fuzzy_list}

    # 4) BM25
    bm25_scores = {}
    for v in variants:
        toks = v.split()
        scores = bm25.get_scores(toks)
        if (scores.max() - scores.min()) > 0:
            norm = (scores - scores.min()) / (scores.max() - scores.min())
        else:
            norm = np.zeros_like(scores)
        for i, s in enumerate(norm):
            bm25_scores[i] = max(bm25_scores.get(i,0), float(s))

    # 5) ترکیب و انتخاب
    combo = combine_scores(emb_scores, fuzzy_scores, bm25_scores, w=(0.65,0.25,0.10))
    top = combo[:k_final]

    # 6) ساخت خروجی شبیه متادیتا
    results = []
    for i, s in top:
        row = metadata.iloc[int(i)].to_dict() if hasattr(metadata, "iloc") else dict(metadata[int(i)])
        row["hybrid_score"] = round(float(s),4)
        row["_index_id"] = int(i)
        results.append(row)
    return results
