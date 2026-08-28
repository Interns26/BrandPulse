"""
Dump every post's FULL text, grouped by cluster, into a readable text
file so you can manually read through and sanity-check that each
cluster actually makes sense.

USAGE (inside backend container):
    docker compose run --rm backend python scripts/export_clusters_readable.py

Output: clusters_readable.txt (in backend/, bind-mounted -- open it
in VS Code / Notepad directly from your host machine).
"""

import pickle


def main():
    with open("post_embeddings.pkl", "rb") as f:
        emb_data = pickle.load(f)
    with open("post_clusters.pkl", "rb") as f:
        cluster_data = pickle.load(f)

    texts = emb_data["texts"]
    labels = cluster_data["labels"]

    clusters = {}
    for idx, label in enumerate(labels):
        clusters.setdefault(label, []).append(idx)

    sorted_labels = sorted(
        [l for l in clusters if l != -1],
        key=lambda l: len(clusters[l]),
        reverse=True,
    )

    with open("clusters_readable.txt", "w", encoding="utf-8") as out:
        for label in sorted_labels:
            indices = clusters[label]
            out.write(f"{'=' * 70}\n")
            out.write(f"CLUSTER {label} -- {len(indices)} posts\n")
            out.write(f"{'=' * 70}\n\n")
            for i, idx in enumerate(indices, 1):
                out.write(f"--- Post {i} ---\n")
                out.write(texts[idx].strip() + "\n\n")

        if -1 in clusters:
            noise_idx = clusters[-1]
            out.write(f"{'=' * 70}\n")
            out.write(f"NOISE -- {len(noise_idx)} posts (not clustered)\n")
            out.write(f"{'=' * 70}\n\n")
            for i, idx in enumerate(noise_idx, 1):
                out.write(f"--- Post {i} ---\n")
                out.write(texts[idx].strip() + "\n\n")

    print("Saved clusters_readable.txt -- open it and read through each cluster.")
    print(f"Total clusters: {len(sorted_labels)}, noise posts: {len(clusters.get(-1, []))}")


if __name__ == "__main__":
    main()