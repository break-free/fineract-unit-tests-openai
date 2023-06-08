import json
import os
import sys
import tiktoken

# Check that environment variables are set up.
if "OPENAI_API_KEY" not in os.environ:
    print("You must set an OPENAI_API_KEY using the Secrets tool", file=sys.stderr)
# Load lists
with open('chunks.json', 'r') as f:
    chunks = json.load(f)

str_chunks = []
for chunk in chunks:
#    s = ("; ").join([chunk['package'],
#                     chunk['type'],
#                     chunk['typename'],
#                     chunk['member'],
#                     chunk['membername'],
#                     chunk['code']])
    str_chunks.append(str(chunk))

print(str_chunks)
