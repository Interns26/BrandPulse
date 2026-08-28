"""
Validate clusters properly: aggregate intra-cluster vs inter-cluster
cosine similarity (not just one anecdotal pair), plus HDBSCAN's own
built-in cluster stability score (cluster_persistence_).

USAGE (inside backend container):
    docker compose run --rm backend python scripts/validate_clusters.py
"""

import itertools
import pickle

import hdbscan
import numpy as np


def cosine_sim_matrix(vectors):
    # vectors are already L2-normalized (normalize_embeddings=True at
    # embed time), so dot product == cosine similarity
    return vectors @ vectors.T


def main():
    with open("post_embeddings.pkl", "rb") as f:
        emb_data = pickle.load(f)
    with open("post_clusters.pkl", "rb") as f:
        cluster_data = pickle.load(f)

    embeddings = np.array(emb_data["embeddings"])
    labels = np.array(cluster_data["labels"])

    cluster_ids = sorted(set(labels) - {-1})

    # --- 1. Aggregate intra-cluster similarity per cluster ---
    print("=== Intra-cluster similarity (avg pairwise cosine sim WITHIN each cluster) ===")
    intra_sims = {}
    for cid in cluster_ids:
        idx = np.where(labels == cid)[0]
        vecs = embeddings[idx]
        sims = cosine_sim_matrix(vecs)
        # exclude diagonal (self-similarity = 1.0)
        n = len(idx)
        off_diag_sum = sims.sum() - np.trace(sims)
        avg = off_diag_sum / (n * (n - 1))
        intra_sims[cid] = avg
        print(f"  Cluster {cid} ({n} posts): avg intra-cluster similarity = {avg:.4f}")

    # --- 2. Aggregate inter-cluster similarity (avg across ALL cross-cluster pairs) ---
    print()
    print("=== Inter-cluster similarity (avg pairwise cosine sim ACROSS different clusters) ===")
    inter_sims = []
    for c1, c2 in itertools.combinations(cluster_ids, 2):
        idx1 = np.where(labels == c1)[0]
        idx2 = np.where(labels == c2)[0]
        sims = embeddings[idx1] @ embeddings[idx2].T
        avg = sims.mean()
        inter_sims.append(avg)
        print(f"  Cluster {c1} vs Cluster {c2}: avg similarity = {avg:.4f}")

    overall_intra = np.mean(list(intra_sims.values()))
    overall_inter = np.mean(inter_sims)
    print()
    print(f"OVERALL: avg intra-cluster similarity = {overall_intra:.4f}")
    print(f"OVERALL: avg inter-cluster similarity  = {overall_inter:.4f}")
    print(f"--> Intra should be clearly higher than inter. Gap = {overall_intra - overall_inter:.4f}")

    # --- 3. HDBSCAN's own stability score per cluster ---
    print()
    print("=== HDBSCAN cluster persistence (built-in stability score, 0-1, higher = more stable) ===")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=5,
        cluster_selection_method="leaf",
        metric="euclidean",
    )
    clusterer.fit(embeddings)
    for cid in cluster_ids:
        if cid < len(clusterer.cluster_persistence_):
            print(f"  Cluster {cid}: persistence = {clusterer.cluster_persistence_[cid]:.4f}")


if __name__ == "__main__":
    main()