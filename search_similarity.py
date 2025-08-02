import os
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

EMBEDDINGS_DIR = "embeddings_data"
EMBEDDINGS_FILE = os.path.join(EMBEDDINGS_DIR, "question_embeddings.npy")
METADATA_FILE = os.path.join(EMBEDDINGS_DIR, "metadata.pkl")
FAISS_INDEX_FILE = os.path.join(EMBEDDINGS_DIR, "faiss_index.idx")

SIMILARITY_THRESHOLD = 0.6

def load_components():
    model = SentenceTransformer("myrkur/sentence-transformer-parsbert-fa-2.0")
    question_embeddings = np.load(EMBEDDINGS_FILE)
    metadata = pd.read_pickle(METADATA_FILE)
    index = faiss.read_index(FAISS_INDEX_FILE)
    return model, metadata, index

def find_similar_questions(query, top_k=10):
    model, metadata, index = load_components()
    query_embedding = model.encode([query], normalize_embeddings=True, convert_to_numpy=True).astype('float32')
    scores, indices = index.search(query_embedding, top_k)

    results = []
    for i in range(top_k):
        idx = indices[0][i]
        score = float(scores[0][i])
        if score >= SIMILARITY_THRESHOLD:
            results.append({
                **metadata[idx],
                "similarity_score": score
            })

    return results
