import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

script_dir = os.path.dirname(os.path.abspath(__file__))
qa_data = os.path.join(script_dir, '..', '..', '..', 'Data', 'ML', 'QA_Base.json')
qa_data = os.path.normpath(qa_data)


# Load model and data
model = SentenceTransformer('all-MiniLM-L6-v2')
with open(qa_data, "r") as f:
    data = json.load(f)

questions = [d["query"] for d in data]
answers = [d["answer"] for d in data]
embeddings = model.encode(questions)

# Create FAISS index
dimension = embeddings[0].shape[0]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# Query function
def get_response(query):
    query_embedding = model.encode([query])
    _, indices = index.search(np.array(query_embedding), 1)
    return [(questions[i], answers[i]) for i in indices[0]]


# Test
print(get_response("What is the battery type of X200?"))
