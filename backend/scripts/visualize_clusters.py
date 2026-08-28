"""
Reduce embeddings to 2D with PCA and plot clusters as a scatter plot,
saved as a PNG for the slide.

USAGE (inside backend container):
    docker compose run --rm backend python scripts/visualize_clusters.py

Output: cluster_plot.png (in backend/, since that's bind-mounted to
your host filesystem -- open it directly from Windows Explorer /
VS Code after running).
"""

import pickle

import matplotlib
matplotlib.use("Agg")  # no display available inside the container
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

# Human-readable names -- edit these to match what you saw in your
# cluster output (check cluster_posts.py output to confirm which
# label number is which topic before presenting).
CLUSTER_NAMES = {
    0: "Music Recommendations",
    1: "r/Python Daily Threads",
    2: "AI / ChatGPT Discussion",
    3: "PC Hardware & Troubleshooting",
    4: "Windows OS Trivia",
    -1: "Noise / Off-topic",
}


def main():
    with open("post_embeddings.pkl", "rb") as f:
        emb_data = pickle.load(f)
    with open("post_clusters.pkl", "rb") as f:
        cluster_data = pickle.load(f)

    embeddings = np.array(emb_data["embeddings"])
    labels = np.array(cluster_data["labels"])

    print("Reducing 384 dims -> 2D with PCA...")
    coords = PCA(n_components=2, random_state=42).fit_transform(embeddings)

    plt.figure(figsize=(10, 7))

    unique_labels = sorted(set(labels))
    for lbl in unique_labels:
        idx = labels == lbl
        name = CLUSTER_NAMES.get(lbl, f"Cluster {lbl}")
        if lbl == -1:
            # noise: small, gray, background
            plt.scatter(coords[idx, 0], coords[idx, 1], s=15, c="lightgray",
                        label=f"{name} ({idx.sum()})", alpha=0.4)
        else:
            plt.scatter(coords[idx, 0], coords[idx, 1], s=35,
                        label=f"{name} ({idx.sum()})", alpha=0.8)

    plt.title("Narrative Clusters Discovered in Reddit Posts (BGE embeddings + HDBSCAN)")
    plt.xlabel("PCA dimension 1")
    plt.ylabel("PCA dimension 2")
    plt.legend(loc="best", fontsize=9)
    plt.tight_layout()
    plt.savefig("cluster_plot.png", dpi=150)
    print("Saved cluster_plot.png")


if __name__ == "__main__":
    main()