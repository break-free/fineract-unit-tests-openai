# Creating Apache Fineract unit tests using OpenAI
:toc:

_Using the existing set of Apache Fineract unit tests, fine tune an OpenAI model using the OpenAI API to generate additional and replacement unit tests._

## Introduction

Note that this repository is more "playground" than anything. In other words, there is a bunch or related and somewhat unrelated files. The instructions contained in this README are kept up to date as much as possible.

## Contributing

Note that the `main` branch is locked down but does allow merge requests (without approvals). Therefore, to make changes and update create a feature or fix branch (prepended with `feature_` or `fix_` respectively). Make your changes there and then when ready, merge your branch into `main` then delete the branch (please we don't need lots of left-over branches!).

## Set Up

Refer to the https://github.com/break-free/fineract-unit-tests-openai/blob/fix_use-token-counters/setup/README.adoc[setup README] for details.

## Converse with OpenAI API Chat using *.java files _contextually_

Note that this approach does not use a fine-tuned model but prompt engineering instead.

1. Parse the code files in `training/test` then chunk them into a list. The code files are used to generate "chunks" by Java package, type, and member. Each chunk also contains useful metadata to describe how the code relates to the application. Three JSON files are created: `chunks.json`, `training_data.json`, and `failed_files.json`. Use the following command:

    $ python3 chunk.py training/test

1. The next step is to "train" a vectorstore using OpenAI embeddings, which creates an embedding (i.e., vector) for each chunk. This allows for similarity searching and to quickly find relevant chunks based on a question. The files created are `faiss.pkl` and `training.index`. Note that the three files outputed in the previous step are required.

    $ python3 train.py

1. The final step is to interact with a chat prompt to generate unit tests. A set of standard, consistent questions are available in `results/basic_questions.adoc` however, other questions may be asked about the application code. Note that the master prompt from `training/unit-tests.prompt` is also used and can be updated to refine results. To start the prompt use the following command:

    $ python3 prompt.py

Following the steps above should yield a similar response to the below image.

image::results/202306091608_fix_readme-and-misc-org.jpeg[]

## Folders

Note that:

* `training/``: contains all training files (i.e., *.java test files) and any prompts.
* `results/`: contains results of tests and questions that generated those results.
* `archive/`: contains any files not used from previous iterations but kept around just in case. Note that these may be used as is however, likely require some modification.

## TODO

- [ ] Refactoring across the board, particularly to reduce the number of called Python scripts.
- [ ] Establish a standard way of calculating token limits.
- [ ] Use token limits to dynamically adjust the amount of context and therefore the number of tokens used during a prompt/completion instance with OpenAI.
- [ ] Containerize this solution so we can deploy it; one for parsing and chunking, another for creating a vector-store and prompting (or something like it).

## Previous README

Additional information that may be useful in the future. Original README is [located here](https://replit.com/@DavidAtReplit/Custom-Company-Chatbot?v=1#README.md).

### JSON API (Advanced Users and not used here)

Option 3, or stating automatically after five seconds on the menu, is the JSON API. You can use POST requests to this Repl's repl.co address to take the chat to a different location or app.

Here's a quick guide to dealing with the API part in Python

    import requests

data to be sent to the server

    data = {'key': 'YOUR API KEY', 'question': 'Your question', 'history': 'previous questioning history'}

sending post request and saving response as response object

    r = requests.post(url = URL, data = data)

extracting response json

    response_data = r.json()

printing response

    print(response_data)
