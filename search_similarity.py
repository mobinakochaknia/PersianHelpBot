# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# ===== مسیر فایل‌ها =====
EMBEDDINGS_DIR = "embeddings_data"
EMBEDDINGS_FILE = os.path.join(EMBEDDINGS_DIR, "question_embeddings.npy")  # شکل: (N, D)
METADATA_FILE = os.path.join(EMBEDDINGS_DIR, "metadata.pkl")               # DataFrame یا list[dict]
FAISS_INDEX_FILE = os.path.join(EMBEDDINGS_DIR, "faiss_index_ip.idx")      # ایندکس جدید (IP)

# ===== تنظیمات =====
MODEL_NAME = "myrkur/sentence-transformer-parsbert-fa-2.0"
SIMILARITY_THRESHOLD = 0.7
TOP_K = 10

# ------------------------------------------------------------
# ابزارها
# ------------------------------------------------------------
def _load_metadata(meta_path):
    """metadata می‌تونه DataFrame یا list[dict] باشه؛ هر دو رو ساپورت کن."""
    meta = pd.read_pickle(meta_path)
    return meta

def _row_to_dict(meta, idx):
    """سطر متادیتا رو به dict برگردون."""
    if isinstance(meta, pd.DataFrame):
        return meta.iloc[int(idx)].to_dict()
    elif isinstance(meta, (list, tuple)):
        return dict(meta[int(idx)])
    else:
        # شیء ناشناخته؛ تلاش می‌کنیم مثل dict رفتار کند
        row = meta[int(idx)]
        return row if isinstance(row, dict) else dict(row)

def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)

# ------------------------------------------------------------
# 1) بازسازی ایندکس تمیز: normalize + IndexFlatIP
# ------------------------------------------------------------
def normalize_and_reindex(
    embeddings_file=EMBEDDINGS_FILE,
    index_file=FAISS_INDEX_FILE
):
    """
    امبدینگ‌های ذخیره‌شده را واحد-نرمال می‌کند و IndexFlatIP می‌سازد.
    خروجی: فایل ایندکس جدید با معیار IP (کساین سیمیلاتی وقتی بردارها نرمال باشند).
    """
    _ensure_dir(os.path.dirname(index_file))
    emb = np.load(embeddings_file).astype('float32')   # (N, D)

    if emb.ndim != 2:
        raise ValueError(f"شکل امبدینگ نامعتبر است: {emb.shape} (باید 2بعدی باشد)")

    # واحد-نرمال‌سازی همهٔ بردارها (خیلی مهم)
    faiss.normalize_L2(emb)

    d = emb.shape[1]
    index = faiss.IndexFlatIP(d)  # IP = inner product
    index.add(emb)
    faiss.write_index(index, index_file)

    return {
        "num_vectors": emb.shape[0],
        "dim": d,
        "index_path": index_file,
        "metric": "IP (cosine when vectors are unit-normalized)"
    }

# ------------------------------------------------------------
# 2) لود کامپوننت‌ها برای سرچ
# ------------------------------------------------------------
def load_components(
    model_name=MODEL_NAME,
    metadata_file=METADATA_FILE,
    index_file=FAISS_INDEX_FILE
):
    model = SentenceTransformer(model_name)
    metadata = _load_metadata(metadata_file)
    index = faiss.read_index(index_file)

    # یک چک کوچک برای اینکه ایندکس، IP باشد
    metric_type = getattr(index, "metric_type", None)
    if metric_type is not None and metric_type != faiss.METRIC_INNER_PRODUCT:
        raise ValueError("ایندکس فعلی با متریک غیر از IP ساخته شده. لطفاً normalize_and_reindex را اجرا کنید.")

    return model, metadata, index

# ------------------------------------------------------------
# 3) جستجوی شباهت با آستانهٔ کساین
# ------------------------------------------------------------
def find_similar_questions(query, top_k=TOP_K, threshold=SIMILARITY_THRESHOLD):
    """
    خروجی: لیستی از رکوردهای متادیتا + similarity_score در بازهٔ [0, 1]
    فقط مواردی که سیمیلاتیشون >= threshold باشند.
    """
    model, metadata, index = load_components()
    q = model.encode([query], normalize_embeddings=True, convert_to_numpy=True).astype('float32')  # واحد-نرمال

    scores, indices = index.search(q, top_k)
    scores = scores[0]    # شکل: (top_k,)
    indices = indices[0]  # شکل: (top_k,)

    results = []
    for rank in range(len(indices)):
        idx = int(indices[rank])
        if idx < 0:
            continue
        sim = float(scores[rank])  # چون IP + بردارها نرمال -> کساین
        if sim >= threshold:
            row_dict = _row_to_dict(metadata, idx)
            results.append({
                **row_dict,
                "similarity_score": round(sim, 4),
                "rank": rank + 1,
                "index_id": idx
            })

    return results

# ------------------------------------------------------------
# 4) نمونهٔ استفاده (اختیاری)
# ------------------------------------------------------------
if __name__ == "__main__":
    # یکبار ایندکس را تمیز بساز (یا وقتی امبدینگ‌ها تغییر کردند)
    info = normalize_and_reindex(EMBEDDINGS_FILE, FAISS_INDEX_FILE)
    print("Reindex info:", info)

    # نمونهٔ سرچ
    query = "چطور مرخصی استعلاجی ثبت کنم؟"
    hits = find_similar_questions(query, top_k=10, threshold=0.7)
    for h in hits:
        print(h["rank"], h["similarity_score"], h.get("question", ""), "->", h.get("answer", "")[:60], "...")
