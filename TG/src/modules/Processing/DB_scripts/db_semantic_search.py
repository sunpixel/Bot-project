import sqlite3, faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Union, Tuple
from TG.src.modules.Optional.enums import ProductColumn, FilterOperator
from TG.src.modules.Optional.filter_generator import build_where_clause
from TG.src.config_manager import config



model = SentenceTransformer('all-MiniLM-L6-v2')
dimension = 384


def db_connect():
    return sqlite3.connect(config.db_path)



# 3. FAISS index setup
index = faiss.IndexFlatL2(dimension)


def update_index():
    """Sync database entries with FAISS index"""

    cursor = db_connect().cursor()

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

"""
    Perform semantic search with optional filters
    Args:
        query: Search query string
        k: Number of results to return
        filters: List of (column, operator, value) tuples using ProductColumn/FilterOperator enums
    Returns:
        List of product tuples
"""

def semantic_search(
        query: str,
        k: int = 3,
        filters: List[Tuple[ProductColumn, FilterOperator, Union[str, float, List]]] = None
    ) -> List[Tuple]:

    cursor = db_connect().cursor()

    # Encode query
    query_embedding = model.encode([query])

    # Search FAISS
    distances, indices = index.search(np.array(query_embedding), k)

    # Get results from database
    results1 = []
    for idx in indices[0]:
        if idx >= 0:  # FAISS returns -1 for empty slots
            product_id = product_ids[idx]

            # Build base query
            base_query = """
                SELECT name, details, speed, capacity, min_temp, max_temp, type, price 
                FROM Products WHERE id = ?
            """
            query_params = [product_id]

            # Add additional filters if provided
            if filters:
                where_clause, filter_params = build_where_clause(filters)
                if where_clause:
                    base_query = base_query.replace("WHERE id = ?", f"WHERE id = ? AND {where_clause[6:]}")
                    query_params.extend(filter_params)

            cursor.execute(base_query, query_params)
            if result := cursor.fetchone():
                results1.append(result)

    return results1


def update_product_embedding(product_id: int):
    conn = db_connect()
    cursor = conn.cursor()
    """Generate and update embedding for a specific product"""
    cursor.execute(
        """SELECT name, details, speed, capacity, min_temp, max_temp, type 
           FROM Products WHERE id = ?""",
        (product_id,)
    )
    if product_data := cursor.fetchone():
        text_parts = [
            product_data[0],  # name
            product_data[1],  # details
            f"Speed: {product_data[2]}",
            f"Capacity: {product_data[3]}",
            f"Temperature range: {product_data[4]} to {product_data[5]}",
            f"Type: {product_data[6]}"
        ]
        text = " ".join(str(part) for part in text_parts if part)
        embedding = model.encode([text])[0]
        cursor.execute(
            "UPDATE Products SET embedding = ? WHERE id = ?",
            (embedding.tobytes(), product_id)
        )
        conn.commit()
        update_index()


def update_all_product_embeddings():
    cursor = db_connect().cursor()
    """Update embeddings for all products"""
    cursor.execute("SELECT id FROM Products")
    for (product_id,) in cursor.fetchall():
        update_product_embedding(product_id)

'''
# Example usage
if __name__ == "__main__":
    # Example filtered search (assuming enums are imported)
    results = semantic_search(
        "industrial freezer",
        filters=[
            (ProductColumn.PRICE, FilterOperator.LESS, 1000),
            (ProductColumn.CAPACITY, FilterOperator.GREATER, 50),
            (ProductColumn.TYPE, FilterOperator.EQUAL, "freezer")
        ]
    )
'''