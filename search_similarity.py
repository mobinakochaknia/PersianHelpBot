import os
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# تنظیمات مسیرها
EMBEDDINGS_DIR = "embeddings_data"
EMBEDDINGS_FILE = os.path.join(EMBEDDINGS_DIR, "question_embeddings.npy")
METADATA_FILE = os.path.join(EMBEDDINGS_DIR, "metadata.pkl")
FAISS_INDEX_FILE = os.path.join(EMBEDDINGS_DIR, "faiss_index.idx")


def load_components():
    """بارگذاری مدل و داده‌های ذخیره شده"""
    if not all(os.path.exists(f) for f in [EMBEDDINGS_FILE, METADATA_FILE, FAISS_INDEX_FILE]):
        raise FileNotFoundError("فایل‌های امبدینگ یافت نشدند. لطفاً ابتدا build_embeddings.py را اجرا کنید")

    model = SentenceTransformer("myrkur/sentence-transformer-parsbert-fa-2.0")
    question_embeddings = np.load(EMBEDDINGS_FILE)
    metadata = pd.read_pickle(METADATA_FILE)
    index = faiss.read_index(FAISS_INDEX_FILE)

    return model, metadata, index


def find_similar_question(query, model, index, metadata, top_k=3):
    """جستجوی سوالات مشابه"""
    query_embedding = model.encode([query], convert_to_numpy=True).astype('float32')
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for i in range(top_k):
        idx = indices[0][i]
        results.append({
            **metadata[idx],
            "similarity_score": float(1 - distances[0][i]),
            "rank": i + 1
        })

    return results


if __name__ == "__main__":
    try:
        model, metadata, index = load_components()

        # مثال جستجو
        query = input("لطفاً سوال خود را وارد کنید: ")
        results = find_similar_question(query, model, index, metadata)

        print(f"\nنتایج برای سوال: '{query}'\n")
        for res in results:
            print(f"""رتبه {res['rank']} (شباهت: {res['similarity_score']:.2f}):
سوال: {res['question']}
پاسخ: {res['answer']}
---""")

    except Exception as e:
        print(f"خطا: {str(e)}")