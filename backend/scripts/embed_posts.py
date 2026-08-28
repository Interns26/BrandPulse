"""
Step 1: Pull Reddit posts from Postgres and embed them with BGE.

USAGE (run inside the backend container, not on the host):
    docker compose run --rm backend python scripts/embed_posts.py

Add these two lines to backend/requirements.txt first, then rebuild:
    sentence-transformers
    hdbscan

CONFIG:
  - DATABASE_URL is read from the DATABASE_URL env var (already set in
    your .env / docker-compose, host "postgres" resolves inside the
    Docker network). No need to edit anything below.
"""

import os
import pickle
import sys

from sqlalchemy import create_engine, text

# ---------------- CONFIG ----------------
DATABASE_URL = os.environ["DATABASE_URL"]
TABLE_NAME = "posts"
ID_COLUMN = "id"
TEXT_COLUMN = "ai_input_text"
LIMIT = 500                    # cap for speed; raise if you have time
MODEL_NAME = "BAAI/bge-small-en-v1.5"
OUTPUT_PATH = "post_embeddings.pkl"
# -----------------------------------------


def fetch_posts():
    engine = create_engine(DATABASE_URL)
    query = text(
        f"SELECT {ID_COLUMN}, {TEXT_COLUMN} FROM {TABLE_NAME} "
        f"WHERE {TEXT_COLUMN} IS NOT NULL AND {TEXT_COLUMN} != '' "
        f"ORDER BY {ID_COLUMN} DESC LIMIT {LIMIT}"
    )
    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()
    if not rows:
        print(f"No rows returned from {TABLE_NAME}.{TEXT_COLUMN} -- check CONFIG.")
        sys.exit(1)
    ids = [r[0] for r in rows]
    texts = [r[1] for r in rows]
    print(f"Fetched {len(texts)} posts.")
    return ids, texts


def embed(texts):
    from sentence_transformers import SentenceTransformer

    print(f"Loading model {MODEL_NAME} (first run downloads it, ~1-2 min)...")
    model = SentenceTransformer(MODEL_NAME)
    print("Embedding posts...")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    return embeddings


def main():
    ids, texts = fetch_posts()
    embeddings = embed(texts)

    with open(OUTPUT_PATH, "wb") as f:
        pickle.dump({"ids": ids, "texts": texts, "embeddings": embeddings}, f)

    print(f"Saved {len(ids)} embeddings (dim={embeddings.shape[1]}) to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()