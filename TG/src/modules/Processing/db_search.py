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
db_path = os.path.join(script_dir, '..', 'Data', 'DataBase', 'products.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 3. Create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    specifications TEXT,
    embedding BLOB  # Store serialized embeddings
)
''')
conn.commit()

# 4. FAISS index setup
index = faiss.IndexFlatL2(dimension)


def update_index():
    """Sync database entries with FAISS index"""
    cursor.execute("SELECT id, embedding FROM products")
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


# 5. Search function
def semantic_search(query, k=3):
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
                "SELECT name, description FROM products WHERE id = ?",
                (product_id,)
            )
            results.append(cursor.fetchone())

    return results


# 6. Insert/update function
def update_product(product_data):
    # Generate embedding
    text = f"{product_data['name']} {product_data['description']} {product_data.get('specifications', '')}"
    embedding = model.encode([text])[0]

    # Store in database
    cursor.execute('''
        INSERT OR REPLACE INTO products 
        (id, name, description, specifications, embedding)
        VALUES (COALESCE((SELECT id FROM products WHERE name = ?), NULL), ?, ?, ?, ?)
    ''', (
        product_data['name'],
        product_data['name'],
        product_data['description'],
        product_data.get('specifications', ''),
        embedding.tobytes()  # Store as binary
    ))
    conn.commit()
    update_index()  # Refresh index