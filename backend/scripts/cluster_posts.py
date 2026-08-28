"""
Step 2: Cluster the saved embeddings with HDBSCAN and print out each
cluster with sample posts, so we can eyeball whether they're coherent.

USAGE (inside backend container):
    docker compose run --rm backend python scripts/cluster_posts.py

CONFIG:
  - MIN_CLUSTER_SIZE: smallest group HDBSCAN will call a cluster
    (rather than lump into noise/-1). Start at 5 for ~500 posts;
    raise it if you get too many tiny/junk clusters, lower it if
    everything gets dumped into noise.
  - MIN_SAMPLES: how conservative the algorithm is about calling
    something noise. Leave at None (defaults to MIN_CLUSTER_SIZE)
    unless you want tighter/looser clusters after seeing the first
    pass.
"""

import pickle

import hdbscan
import numpy as np

# ---------------- CONFIG ----------------
INPUT_PATH = "post_embeddings.pkl"
MIN_CLUSTER_SIZE = 5
MIN_SAMPLES = None
SAMPLES_PER_CLUSTER = 4
# -----------------------------------------


def main():
    with open(INPUT_PATH, "rb") as f:
        data = pickle.load(f)

    ids = data["ids"]
    texts = data["texts"]
    embeddings = np.array(data["embeddings"])

    print(f"Clustering {len(texts)} posts...")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=MIN_CLUSTER_SIZE,
        min_samples=MIN_SAMPLES,
        metric="euclidean",
        cluster_selection_method="leaf",
    )
    labels = clusterer.fit_predict(embeddings)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = int(np.sum(labels == -1))
    print(f"Found {n_clusters} clusters, {n_noise} posts labeled as noise (-1)")
    print()

    # Group post indices by cluster label
    clusters = {}
    for idx, label in enumerate(labels):
        clusters.setdefault(label, []).append(idx)

    # Print clusters sorted by size (biggest first), noise last
    sorted_labels = sorted(
        [l for l in clusters if l != -1],
        key=lambda l: len(clusters[l]),
        reverse=True,
    )

    for label in sorted_labels:
        indices = clusters[label]
        print(f"=== Cluster {label} ({len(indices)} posts) ===")
        for idx in indices[:SAMPLES_PER_CLUSTER]:
            print(f"  - {texts[idx][:150]}")
        print()

    if -1 in clusters:
        print(f"=== Noise ({len(clusters[-1])} posts) === (sample)")
        for idx in clusters[-1][:SAMPLES_PER_CLUSTER]:
            print(f"  - {texts[idx][:150]}")

    # Save cluster assignments alongside the embeddings for later use
    with open("post_clusters.pkl", "wb") as f:
        pickle.dump({"ids": ids, "texts": texts, "labels": labels}, f)
    print()
    print("Saved cluster assignments to post_clusters.pkl")


if __name__ == "__main__":
    main()