from data_chunker import parser
from data_chunker import java_code as JCC
import faiss
import json
from langchain import OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import Prompt
from langchain.vectorstores import FAISS
import os
import sys
import tiktoken

# Print parsing statistics
def print_parsing_statistics(t: list, f: list):
    attempts = len(t)
    failures = len(f)
    print("Number of files attempted to be parsed = " + str(attempts))
    print("Number of failed files = " + str(failures) +
          ", Failure rate = " + "{:.2f}".format(failures/attempts*100) + "%")

def print_token_statistics(chunks: list):
    # Print token statistics
    encoding = tiktoken.get_encoding("cl100k_base")
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_member_tokens = num_method_tokens = max_tokens = num_method_chunks = 0
    num_member_chunks = len(chunks)
    max_chunk = None
    max_chunks = []
    token_limit = 1600
    for chunk in chunks:
        tokens = len(encoding.encode(str(chunk)))
        num_member_tokens = num_member_tokens + tokens
        if chunk['member'] == "method":
            num_method_tokens = num_method_tokens + tokens
            num_method_chunks = num_method_chunks + 1
        if tokens > max_tokens:
            max_tokens = tokens
            max_chunk = chunk
        if tokens > token_limit:
            max_chunks.append({chunk['typename'], chunk['membername'], tokens})
    print("Number of chunks generated = " + str(num_member_chunks))
    print("Average number of tokens per chunk = " + 
          "{:.2f}".format(num_member_tokens/num_member_chunks))
    print("Average number of tokens per method chunk = " +
          "{:.2f}".format(num_method_tokens/num_method_chunks))
    print("Maximum token size = " + str(max_tokens))
    print("Number of chunks over " + str(token_limit) + " is " + str(len(max_chunks)))
    #for chunk in max_chunks:
    #    print(chunk)

def print_chunks_sample(chunks: list):
    print("Chunks sample")
    print("-------------")
    for chunk in chunks[:10]:
        print(str(chunk))
    print("...")

def train(chunks:list):
    str_chunks = []
    for chunk in chunks:
        str_chunks.append(str(chunk))

    return FAISS.from_texts(str_chunks, OpenAIEmbeddings())

def chunk(file_path:str, fileExtension:str):
    # Retrieve file list and initialize lists
    data = parser.get_file_list(file_path, fileExtension)
    chunks = []
    failed_files = []
    # Chunk data using the files in the training data
    if fileExtension == "*.java":
        for file in data:
            codelines = parser.get_code_lines(file)
            try:
                tree = JCC.parse_code(file, codelines)
            except JCC.ParseError as e:
                failed_files.append(str(file) + ": " + str(e))
            if tree != None:
                try:
                    chunks = chunks + JCC.chunk_constants(tree)
                    chunks = chunks + JCC.chunk_constructors(tree, codelines)
                    chunks = chunks + JCC.chunk_fields(tree, codelines)
                    chunks = chunks + JCC.chunk_methods(tree, codelines)
                except JCC.ChunkingError as e:
                    failed_files.append(str(file) + ": " + str(e))
            else:
                failed_files.append(str(file) + ", has no tree!")
    else:
        print(f'''File extension type "{fileExtension}" is currently not supported.''')
        exit()

    return data, chunks, failed_files

def prompter(store, master_prompt_path:str, show_context:bool=False):

    with open(master_prompt_path, "r") as f:
        promptTemplate = f.read()
    prompt = Prompt(template=promptTemplate, 
                    input_variables=["context", "question", "history"])
    llmChain = LLMChain(prompt=prompt, 
                        llm=ChatOpenAI(model="gpt-3.5-turbo",temperature=0))

    def onMessage(question, history):
        # Retrieve chunks based on the question and assemble them into a 
        # joined context.
        chunks = store.similarity_search(question)
        contexts = []
        for i, chunk in enumerate(chunks):
            contexts.append(f"Context {i}:\n{chunk.page_content}")
        if show_context:
            joined_contexts = "\n\n".join(contexts)
            print(f"Context Provided:\n {joined_contexts}")
        joined_contexts = "\n\n".join(contexts)
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
        question = input("\nAsk a question: ")
        if question == 'exit':
            break
        else:
            answer = onMessage(question, history)
            history = history + answer +"\n\n###\n\n"
            print(f"\nBot: {answer}")
            print("Answer tokens: " + str(llmChain.llm.get_num_tokens(answer)))
