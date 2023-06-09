import faiss
import json
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import os
import pickle
import sys

# Check that environment variables are set up.
if "OPENAI_API_KEY" not in os.environ:
    print("You must set an OPENAI_API_KEY using the Secrets tool", file=sys.stderr)
# Load lists
with open('chunks.json', 'r') as f:
    chunks = json.load(f)

str_chunks = []
for chunk in chunks:
    str_chunks.append(str(chunk))

store = FAISS.from_texts(str_chunks, OpenAIEmbeddings())
faiss.write_index(store.index, "training.index")
store.index = None

with open("faiss.pkl", "wb") as f:
    pickle.dump(store, f)
