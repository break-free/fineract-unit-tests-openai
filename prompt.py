import faiss
import json
from langchain import OpenAI, LLMChain
from langchain.prompts import Prompt
import pickle

# Check that environment variables are set up.
if "OPENAI_API_KEY" not in os.environ:
    print("You must set an OPENAI_API_KEY using the Secrets tool", file=sys.stderr)
# Load the store.
index = faiss.read_index("training.index")
with open("faiss.pkl", "rb") as f:
    store = pickle.load(f)
store.index = index

with open("training/unit-test.prompt", "r") as f:
    promptTemplate = f.read()
prompt = Prompt(template=promptTemplate, input_variables=["context", "question", "history"])
llmChain = LLMChain(prompt=prompt, llm=OpenAI(temperature=0.1))

def onMessage(question, history):
    chunks = store.similarity_search(question)
    contexts = []
    for i, chunk in enumerate(chunks):
        contexts.append(f"Context {i}:\n{chunk.page_content}")

    with open('contexts.json', 'w') as f:
        json.dump(contexts, f)
    
    return llmChain.predict(question=question, 
                            context="\n\n".join(contexts),
                            history=history)

history = ""
while True:
    question = input("Ask a question > ")
    if question == 'exit':
        break
    else:
        answer = onMessage(question, history)
        history = history + answer +"\n\n###\n\n"
        print(f"Bot: {answer}")
