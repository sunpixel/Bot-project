import json
import numpy as np
import torch
import faiss
import os
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM



# === CONFIG ===
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL_PATH = os.path.abspath(os.path.join("TG", "Data", "Models", "phi-2")) # Can be downloaded here https://huggingface.co/microsoft/phi-2/tree/main
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# === LOAD MODELS ===
print("Loading embedding model...")
embedder = SentenceTransformer(EMBED_MODEL_NAME)

print("Loading local Phi-2 model...")
tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(
    LLM_MODEL_PATH,
    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
)
model.to(DEVICE)

# === LOAD QA DATA ===
with open("qa_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

questions = [d["question"] for d in data]
answers = [d["answer"] for d in data]

# === EMBEDDINGS + FAISS INDEX ===
print("Generating embeddings...")
question_embeddings = embedder.encode(questions)

index = faiss.IndexFlatL2(question_embeddings[0].shape[0])
index.add(np.array(question_embeddings))


# === HYBRID RESPONSE FUNCTION ===
def get_response(user_query):
    query_embedding = embedder.encode([user_query])
    _, top_indices = index.search(np.array(query_embedding), 3)

    # Build context from top answers
    context = "\n".join([answers[i] for i in top_indices[0]])

    prompt = f"""You are a helpful assistant. Use the context below to answer the question.

Context:
{context}

Question: {user_query}

Answer:"""

    # Tokenize and generate
    inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
        temperature=0.7,
        do_sample=False,
        pad_token_id=tokenizer.eos_token_id,
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.split("Answer:")[-1].strip()


# === TEST ===
if __name__ == "__main__":
    while True:
        query = input("\nAsk a question: ")
        if query.lower() in ["exit", "quit"]:
            break
        print("\nAnswer:", get_response(query))
