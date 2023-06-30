# Creating Unit Tests using OpenAI
## Introduction

The original intent of this codebase was to perform prompt engineering via "vectorization" of a java codebase and then feeding the embedded text to openAI for it to automatically generate unit tests. More languages and LLMs will eventually be supported, and the use cases aren't necessarily limited to unit test generation.

This repository contains several unrelated/experimental files based on past iterations, but in general the module lives in the `src/llm_prompt_creator` directory. 

The instructions in this README are kept up to date as much as possible.

## Contributing

Note that the `main` branch is locked down but does allow merge requests. 

To contribute, create a feature or fix branch (prepended with `feature_` or `fix_` respectively), commit your changes there and then create a pull request from your branch into `main`.

We will review & (after approval) merge your git branch and then delete the remote branch on our github repo to limit left-over branches.

## Set Up

> **Note**
> Windows users may need to install the Visual Studio C++ Compiler to use this package

Simple example usage:
```
from llm_prompt_creator import prompt as PR
dir = "<path to your java codebase directory>"

# Chunk & store your codebase as tokenized chunks via javalang.
# Defaults to store succesfully chunked files in "./chunks.json".
PR.chunker(dir)

# Create a vector store to perform a similarity search against when asking questions to your
# LLM. Defaults to consume from the "./chunks.json" file.
store = PR.create_store()

# Start an open-ended chat conversation with your LLM based on your vector store.
# Will continue prompting the user for inputs until they type 'exit'.
# Subject to model limitations (especially token limits).
PR.prompt(store)

"""
To show the context provided (provided by the vector store based on the user's question)
uncomment the below:
"""
# PR.prompt(store, show_context=True)
```

Following the example should yield a similar response to the below image 
(subject to LLM model used and codebase):

![](results/202306091608_fix_readme-and-misc-org.jpeg)

## TODO

- [x] Refactoring across the board, particularly to reduce the number of called Python scripts.
- [ ] Optimize chunker to allow larger codebase directories
- [ ] Establish a standard way of calculating token limits.
- [ ] Use token limits to dynamically adjust the amount of context and therefore the number of tokens used during a prompt/completion instance with OpenAI.
- [ ] Containerize this solution so we can deploy it; one for parsing and chunking, another for creating a vector-store and prompting (or something like it).