import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

# 1. Initialize components
model = SentenceTransformer('all-MiniLM-L6-v2')
dimension = 384  # Dimension for all-MiniLM-L6-v2

# 2. Database setup
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.abspath(os.path.join(script_dir, '..', '..', '..', 'Data', 'DataBase', 'shop.db'))
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 3. FAISS index setup
index = faiss.IndexFlatL2(dimension)


def update_index():
    """Sync database entries with FAISS index"""
    cursor.execute("SELECT id, embedding FROM Products WHERE embedding IS NOT NULL")
    embeddings = []
    ids = []
    for row in cursor.fetchall():
        ids.append(row[0])
        embeddings.append(np.frombuffer(row[1], dtype=np.float32))

    if embeddings:
        index.reset()
        index.add(np.array(embeddings))
    return ids


# Initial index update
product_ids = update_index()


def semantic_search(query, k=3):
    """
    Perform semantic search on products
    Args:
        query: Search query string
        k: Number of results to return
    Returns:
        List of tuples with product details (name, details, speed, capacity, min_temp, max_temp, type, price)
    """
    # Encode query
    query_embedding = model.encode([query])

    # Search FAISS
    distances, indices = index.search(np.array(query_embedding), k)

    # Get results from database
    results = []
    for idx in indices[0]:
        if idx >= 0:  # FAISS returns -1 for empty slots
            product_id = product_ids[idx]
            cursor.execute(
                """SELECT name, details, speed, capacity, min_temp, max_temp, type, price 
                   FROM Products WHERE id = ?""",
                (product_id,)
            )
            results.append(cursor.fetchone())

    return results


def update_product_embedding(product_id):
    """
    Generate and update embedding for a specific product
    Args:
        product_id: ID of the product to update
    """
    # Get product data
    cursor.execute(
        """SELECT name, details, speed, capacity, min_temp, max_temp, type 
           FROM Products WHERE id = ?""",
        (product_id,)
    )
    product_data = cursor.fetchone()

    if product_data:
        # Generate text for embedding
        text_parts = [
            product_data[0],  # name
            product_data[1],  # details
            f"Speed: {product_data[2]}",  # speed
            f"Capacity: {product_data[3]}",  # capacity
            f"Temperature range: {product_data[4]} to {product_data[5]}",  # temp range
            f"Type: {product_data[6]}"  # type
        ]
        text = " ".join(str(part) for part in text_parts if part)

        # Generate and store embedding
        embedding = model.encode([text])[0]
        cursor.execute(
            "UPDATE Products SET embedding = ? WHERE id = ?",
            (embedding.tobytes(), product_id)
        )
        conn.commit()
        update_index()  # Refresh index


def update_all_product_embeddings():
    """Update embeddings for all products in the database"""
    cursor.execute("SELECT id FROM Products")
    product_ids = [row[0] for row in cursor.fetchall()]

    for product_id in product_ids:
        update_product_embedding(product_id)

# Example usage:
# update_all_product_embeddings()  # Run this when you want to update all embeddings
# results = semantic_search("fast freezer with large capacity")