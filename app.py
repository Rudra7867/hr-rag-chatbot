from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import pickle
import faiss
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# =====================================
# LOAD ENVIRONMENT
# =====================================

load_dotenv()

app = Flask(__name__)
CORS(app)

# =====================================
# GEMINI SETUP
# =====================================

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# =====================================
# LOAD VECTOR DATABASE
# =====================================

print("\nLoading Vector Database...")

index = faiss.read_index("hr_policy.index")

with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("RAG System Ready")
print("Total Chunks Loaded:", len(chunks))

# =====================================
# RAG SEARCH
# =====================================

def search_policy(question, top_k=3):

    query_embedding = embedding_model.encode([question])

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    print("\n")
    print("=" * 70)
    print("QUESTION:")
    print(question)
    print("=" * 70)

    print("\nTOP POLICY CHUNKS RETRIEVED\n")

    for i, idx in enumerate(indices[0]):

        chunk = chunks[idx]

        print(f"\nCHUNK {i+1}")
        print("-" * 50)
        print(chunk[:500])

        results.append(chunk)

    print("\n" + "=" * 70)

    return "\n\n".join(results)

# =====================================
# HOME
# =====================================

@app.route("/")
def home():
    return "AI HR Assistant RAG Running"

# =====================================
# CHAT
# =====================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.json

        question = data["message"]

        policy_context = search_policy(question)

        prompt = f"""
You are an AI HR Assistant.

STRICT RULES:

1. Answer ONLY using the HR Policy context.
2. Do not invent information.
3. Be professional and friendly.
4. Keep answers concise.
5. Maximum 5 lines.
6. Summarize instead of copying.
7. If information is unavailable say:
"This information is not available in the HR Policy."

HR POLICY:

{policy_context}

EMPLOYEE QUESTION:

{question}

ANSWER:
"""

        response = model.generate_content(
            prompt
        )

        answer = response.text

        print("\nANSWER GENERATED:")
        print(answer)
        print("=" * 70)

        return jsonify({
            "reply": answer
        })

    except Exception as e:

        print("ERROR:", str(e))

        return jsonify({
            "reply": f"Error: {str(e)}"
        })

# =====================================
# RUN APP
# =====================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)