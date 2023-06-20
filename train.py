import chromadb
import json
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
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

store = Chroma(collection_name="langchain_store",
               embedding_function=OpenAIEmbeddings(),
               persist_directory="db")
store.add_texts(str_chunks)

print(f"The store count is: {store._collection.count}")

