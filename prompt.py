import faiss
import langchain import OpenAI, LLMChain
import langchain.prompts import Prompt
import pickle

index = faiss.read_index("training.index")

with open("faiss.pkl", "rb") as f:
    store = pickle.load(f)

store.index = index

with open("training/unit-test.prompt", "r") as f:
    promptTemplate = f.read()

prompt = Prompt(template=promptTemplate, input_variables=["context", "question"])

llmChain = LLMChain(prompt=prompt, llm=OpenAI(temperature=0.1))

def onMessage(question, history):
    docs = store.similarity_search(question)
    contexts = []
    for i, doc in enumerate(docs):
        contexts.append(f"Context {i}:\n{doc.page_content}")
        answer = llmChain.predict(question=question, 
                                  context="\n\n".join(contexts))
    return answer

while True:
    question = input("Ask a question > ")
    answer = onMessage(question, history)
    print(f"Bot: {answer}")
