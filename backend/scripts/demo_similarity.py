"""
Terminal demo: show raw embedding vectors, and prove that posts in the
same cluster are semantically closer (higher cosine similarity) than
posts from different clusters. This is the "proof it's a real cluster"
piece for the demo.

USAGE (inside backend container):
    docker compose run --rm backend python scripts/demo_similarity.py
"""

import pickle

import numpy as np


def cosine_sim(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main():
    with open("post_embeddings.pkl", "rb") as f:
        emb_data = pickle.load(f)
    with open("post_clusters.pkl", "rb") as f:
        cluster_data = pickle.load(f)

    texts = emb_data["texts"]
    embeddings = np.array(emb_data["embeddings"])
    labels = cluster_data["labels"]

    # --- 1. Show a raw embedding vector ---
    print("=== Raw embedding vector (post 0, first 10 of 384 dims) ===")
    print(f"Text: {texts[0][:100]}...")
    print(f"Vector: {embeddings[0][:10]}")
    print()

    # --- 2. Compare two posts from the SAME cluster ---
    cluster_ids, counts = np.unique(labels[labels != -1], return_counts=True)
    biggest_cluster = cluster_ids[np.argmax(counts)]
    same_cluster_idx = np.where(labels == biggest_cluster)[0][:2]

    a, b = same_cluster_idx[0], same_cluster_idx[1]
    sim = cosine_sim(embeddings[a], embeddings[b])
    print(f"=== Same cluster (cluster {biggest_cluster}) ===")
    print(f"Post A: {texts[a][:100]}...")
    print(f"Post B: {texts[b][:100]}...")
    print(f"Cosine similarity: {sim:.4f}")
    print()

    # --- 3. Compare two posts from DIFFERENT clusters ---
    other_clusters = [c for c in cluster_ids if c != biggest_cluster]
    other_cluster = other_clusters[0]
    diff_idx = np.where(labels == other_cluster)[0][0]

    sim2 = cosine_sim(embeddings[a], embeddings[diff_idx])
    print(f"=== Different clusters ({biggest_cluster} vs {other_cluster}) ===")
    print(f"Post A: {texts[a][:100]}...")
    print(f"Post C: {texts[diff_idx][:100]}...")
    print(f"Cosine similarity: {sim2:.4f}")
    print()
    print(f"--> Same-cluster similarity ({sim:.4f}) should be noticeably")
    print(f"    higher than cross-cluster similarity ({sim2:.4f})")


if __name__ == "__main__":
    main()