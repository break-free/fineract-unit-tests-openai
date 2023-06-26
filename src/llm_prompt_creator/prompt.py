import json
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import Prompt
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import os
from data_chunker import parser as JCParser
from data_chunker import java_code as JCChunker


# Check that environment variables are set up.
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("You must set an OPENAI_API_KEY environment variable value")

def chunker(directory, file_extension:str="*.java", outdir:str="."):
    """Leverages data-chunker package to parse & chunk text-based code files into LLM-consumable tokens. Currently only supports java (*.java)"""
    
    if file_extension != "*.java":
        raise ValueError("This file type is not supported yet.")

    training_data = list()
    
    training_data = JCParser.get_file_list(directory, file_extension=file_extension)
    # Chunk data using the files in the training data
    chunks = []
    failed_files = []
    for file in training_data:
        codelines = JCParser.get_code_lines(file)
        try:
            tree = JCChunker.parse_code(file, codelines)
        except JCChunker.ParseError as e:
            failed_files.append(str(file) + ": " + str(e))
        if tree != None:
            try:
                chunks = chunks + JCChunker.chunk_constants(tree)
                chunks = chunks + JCChunker.chunk_constructors(tree, codelines)
                chunks = chunks + JCChunker.chunk_fields(tree, codelines)
                chunks = chunks + JCChunker.chunk_methods(tree, codelines)
            except JCChunker.ChunkingError as e:
                failed_files.append(str(file) + ": " + str(e))
        else:
            failed_files.append(str(file) + ", has no tree!")
    
    # Convert training_data paths into strings for serialization.
    training_data_str = list()
    for data in training_data: 
        training_data_str.append(str(data))
    # Save each used list as a file for other operations.
    with open(f"{outdir}/training_data.json", 'w') as f:
        json.dump(training_data_str, f)
    with open(f"{outdir}/chunks.json", 'w') as f:
        json.dump(chunks, f)
    with open(f"{outdir}/failed_files.json", 'w') as f:
        json.dump(failed_files, f)

def create_store(filepath:str="chunks.json", persistdir:str="db", model:str="gpt-3.5-turbo"):
    """Create the vector store to utilize for other commands (currently limited to OpenAI). Consumes filepath (JSON format) that defaults to a local 
    'chunks.json' to match default behavior of data-chunker module. 
    
    Returns a Chroma store."""
    
    #TODO: make an ephemeral option
    #TODO: make a for loop to iterate over a potential suite of JSON files

    str_chunks = []

    with open(filepath, 'r') as f:
        chunks = json.load(f)

    for chunk in chunks:
        str_chunks.append(str(chunk))

    store = Chroma(collection_name="langchain_store",
                embedding_function=OpenAIEmbeddings(model=model),
                persist_directory=persistdir).from_texts(str_chunks, OpenAIEmbeddings(model=model))
        
    return store
    
def search_store(store: Chroma, text: str):
    """Perform a similarity search against the Chroma vector store based on the text provided."""
    store_chunks = store.similarity_search(text)

    return store_chunks

def prompt(store: Chroma, show_context=False, templateDir:str=None):
    """Setup a chat session with the LLM (currently limited to OpenAI). The session maintains history by storing the
    previous answers into a history list and appending them to each future prompt, meaning there is a limit for number of 
    questions per individual session (you will eventually reach the token limit per model).
    
    Will continue the chat session until the user types 'exit' as their prompt."""

    history = ""

    # Load the promptTemplate for model context :
    if templateDir != None:
        with open(templateDir, "r") as f:
            promptTemplate = f.read()
    else:
        promptTemplate = """You are a world-class Java developer with an eagle eye for unintended bugs and edge cases. You carefully explain code with great detail and accuracy. You organize your explanations in markdown-formatted, bulleted lists.
        You write careful, accurate unit tests. When asked to reply only with code, you write all of your code in a single block.
        A good unit test suite should aim to:
        - Test the function's behavior for a wide range of possible inputs
        - Test edge cases that the author may not have foreseen
        - Take advantage of the features of `pytest` to make the tests easy to write and maintain
        - Be easy to read and understand, with clean code and descriptive names
        - Be deterministic, so that the tests always pass or fail in the same way
        Use the following pieces of MemoryContext to answer the question at the end. Also remember ConversationHistory is a list of Conversation objects.
        ---
        ConversationHistory: {history}
        ---
        MemoryContext: {context}
        ---
        Human: {question}
        Bot:"""    
    
    # Retrieve chunks based on the question and assemble them into a joined context:
    """
    Lock the user in a loop to keep asking questions until they type 'exit'
    Add the LLM's answer to the chat history to keep the feedback more conversational
    """
    while True:
        question = input("Ask a question > ")
        if question == 'exit':
            break
        else:
            chunks = search_store(store, question)
            contexts = []
            for i, chunk in enumerate(chunks):
                contexts.append(f"Context {i}:\n{chunk.page_content}")
            with open('contexts.json', 'w') as f:
                json.dump(contexts, f)
            joined_contexts = "\n\n".join(contexts)
            
            prompt = Prompt(template=promptTemplate, input_variables=["context", "question", "history"])
            llmChain = LLMChain(prompt=prompt, llm=ChatOpenAI(model="gpt-3.5-turbo",temperature=0))
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
            
            # Return the prediction.
            answer = llmChain.predict(prompt=prompt,
                            question=question, 
                            context=joined_contexts,
                            history=history)
            history = history + answer +"\n\n###\n\n"
            print(f"Bot: {answer}")
            print("Answer tokens: " + str(llmChain.llm.get_num_tokens(answer)))
