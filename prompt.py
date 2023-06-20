import sys
import json
from langchain import OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import Prompt
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import os

persist_dir = "db"

# Check that environment variables are set up.
if "OPENAI_API_KEY" not in os.environ:
    print("You must set an OPENAI_API_KEY using the Secrets tool", file=sys.stderr)

# Load the store.
store_files = []
for root, dirs, files in os.walk(persist_dir):
    for file in files:
        store_files.append(os.path.join(root, file))

for file in store_files:
    with open(file, "rb") as f:
        store_text = f.read()

store = Chroma.from_texts(embedding=OpenAIEmbeddings(), texts=store_text)

with open("training/unit-test.prompt", "r") as f:
    promptTemplate = f.read()
prompt = Prompt(template=promptTemplate, input_variables=["context", "question", "history"])
llmChain = LLMChain(prompt=prompt, llm=ChatOpenAI(model="gpt-3.5-turbo",temperature=0))

def onMessage(question, history, show_context=False):
    # Retrieve chunks based on the question and assemble them into a 
    # joined context.
    chunks = store.similarity_search(question)
    print(f"Here are all the chunks: {chunks}")
    contexts = []
    for i, chunk in enumerate(chunks):
        print(f"Here's a chunk: {chunk}")
        contexts.append(f"Context {i}:\n{chunk.page_content}")
    with open('contexts.json', 'w') as f:
        json.dump(contexts, f)
    joined_contexts = "\n\n".join(contexts)
    if (show_context):
        print(f"Context Provided: {joined_contexts}")

    # For each message to OpenAI, print tokens used for each part and in total
    question_tokens = llmChain.llm.get_num_tokens(question)
    contexts_tokens = llmChain.llm.get_num_tokens(joined_contexts)
    history_tokens = llmChain.llm.get_num_tokens(history)
    print("Question tokens: " + str(question_tokens) + ", " +
          "Contexts' tokens: " + str(contexts_tokens) + ", " +
          "History tokens: " + str(history_tokens) + ", " +
          "TOTAL: " + str(question_tokens+contexts_tokens+history_tokens))
    # Return the prediction.
    return llmChain.predict(question=question, 
                            context=joined_contexts,
                            history=history)

history = ""
while True:
    if (sys.argv[1] == "Show_Context"):
        show_context=True
    question = input("Ask a question > ")
    if question == 'exit':
        break
    else:
        answer = onMessage(question, history, show_context=show_context)
        history = history + answer +"\n\n###\n\n"
        print(f"Bot: {answer}")
        print("Answer tokens: " + str(llmChain.llm.get_num_tokens(answer)))
