import sys
import json
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import Prompt
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import os


# Check that environment variables are set up.
if "OPENAI_API_KEY" not in os.environ:
    print("You've got nothin' here chief.")
    raise ValueError("You must set an OPENAI_API_KEY environment variable value")

def create_store(directory):
    """Create the vector store to utilize for other commands (currently limited to OpenAI)"""
    
    # Where to store/load the context chunks:
    if directory == None:
        persist_dir = "db"
    else:
        persist_dir = directory

    store = Chroma(collection_name="langchain_store",
                embedding_function=OpenAIEmbeddings(model="gpt-3.5-turbo"),
                persist_directory=persist_dir)
    
    return store
    
def search_store(store: Chroma, text: str):
    """Perform a Chroma similarity search against the vector store based on the text provided"""
    store_chunks = store.similarity_search(text)

    return store_chunks

def prompt(question, show_context=False, template=None):
    """Setup the chat session with the LLM (currently limited to OpenAI)"""

    history = ""

    # Load the promptTemplate for model context:
    if template != None:
        with open(template, "r") as f:
            promptTemplate = f.read()
    else:
        with open("training/unit-test.prompt", "r") as f:
            promptTemplate = f.read()
    prompt = Prompt(template=promptTemplate, input_variables=["context", "question", "history"])
    llmChain = LLMChain(prompt=prompt, llm=ChatOpenAI(model="gpt-3.5-turbo",temperature=0))
    
    # Retrieve chunks based on the question and assemble them into a joined context:
    chunks = search_store(question)
    contexts = []
    for i, chunk in enumerate(chunks):
        contexts.append(f"Context {i}:\n{chunk.page_content}")
    with open('contexts.json', 'w') as f:
        json.dump(contexts, f)
    joined_contexts = "\n\n".join(contexts)
    
    # If user's asked to show the context, provide it to them (chunks of text from their vector store):
    if (show_context):
        print(f"Context Provided: {joined_contexts}")

    # For each message to OpenAI, print tokens used for each part and in total
    question_tokens = llmChain.llm.get_num_tokens(question)
    contexts_tokens = llmChain.llm.get_num_tokens(joined_contexts)
    history_tokens = llmChain.llm.get_num_tokens(history)
    print("Question tokens: " + str(question_tokens) + "\n" +
          "Contexts' tokens: " + str(contexts_tokens) + "\n" +
          "History tokens: " + str(history_tokens) + "\n\n" +
          "TOTAL: " + str(question_tokens+contexts_tokens+history_tokens))
    
    """
    Lock the user in a loop to keep asking questions until they type 'exit'
    Add the LLM's answer to the chat history to keep the feedback more conversational
    """
    while True:
        question = input("Ask a question > ")
        if question == 'exit':
            break
        else:
            # Return the prediction.
            answer = llmChain.predict(prompt=prompt,
                            question=question, 
                            context=joined_contexts,
                            history=history)
            history = history + answer +"\n\n###\n\n"
            print(f"Bot: {answer}")
            print("Answer tokens: " + str(llmChain.llm.get_num_tokens(answer)))
