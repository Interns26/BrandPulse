"""
Quick sanity check on post_embeddings.pkl.

USAGE (inside backend container):
    docker compose run --rm backend python scripts/inspect_embeddings.py
"""

import pickle

with open("post_embeddings.pkl", "rb") as f:
    data = pickle.load(f)

ids = data["ids"]
texts = data["texts"]
embeddings = data["embeddings"]

print(f"Total posts: {len(ids)}")
print(f"Embedding shape: {embeddings.shape}")
print()
print("Sample posts:")
for i in range(3):
    print(f"- id={ids[i]}")
    print(f"  text: {texts[i][:120]}...")
    print(f"  vector (first 5 dims): {embeddings[i][:5]}")
    print()