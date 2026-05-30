from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import pickle

print("Loading PDF...")

reader = PdfReader("HR-Policy-Manual.pdf")

text = ""

for page in reader.pages:
    page_text = page.extract_text()

    if page_text:
        text += page_text + "\n"

print("PDF Loaded")

# Clean text
text = text.replace("\n", " ")
text = " ".join(text.split())

# Split into chunks
chunk_size = 500

chunks = []

for i in range(0, len(text), chunk_size):
    chunks.append(text[i:i + chunk_size])

print("Total Chunks:", len(chunks))

# Load embedding model
print("Loading Embedding Model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Creating Embeddings...")

embeddings = model.encode(chunks)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

faiss.write_index(index, "hr_policy.index")

with open("chunks.pkl", "wb") as f:
    pickle.dump(chunks, f)

print("RAG Index Created Successfully")