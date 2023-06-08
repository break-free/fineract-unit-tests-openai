import json
import os
import sys
import tiktoken

# Check that environment variables are set up.
if "OPENAI_API_KEY" not in os.environ:
    print("You must set an OPENAI_API_KEY using the Secrets tool", file=sys.stderr)
# Load lists
with open('chunks.pkl', 'r') as f:
    chunks_str = f.read()
chunks = ast.literal_eval(chunks_str)

print(chunks)
