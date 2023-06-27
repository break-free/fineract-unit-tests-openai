#!/usr/bin/env python3

import sys, os, openai

def checkInputIsAnInteger(value):
    # Check that the input is an integer and if not keep asking
    try:
        value = int(value)
    except ValueError:
        value = input("Invalid input. Please enter a number: ") 
        value = checkInputIsAnInteger(value)
    return value

def userSelectModel(models):
    
    # Prompt user to select a model
    print("== Choose an OpenAI Model ==")
    count = 1
    for model in models:
        print(str(count)+": "+model)
        count = count + 1
    user_input = input("Enter your selection (1-"+str(len(models))+"): ")
    user_input_int = checkInputIsAnInteger(user_input)

    # Check that input is within range
    while user_input_int > len(models) or user_input_int <= 0:
        user_input = input("Invalid choice, enter your selection: ")
        user_input_int = checkInputIsAnInteger(user_input)

    return models[user_input_int-1]


if __name__ == "__main__":

    # Check that required variables are set.
    if "OPENAI_API_KEY" not in os.environ:
        print("You must set an OPENAI_API_KEY using the Secrets tool", file=sys.stderr)
        sys.exit(1)
    
    # Import models from the models list   
    models = list()
    with open('model-list.txt', 'r') as file:
        for line in file:
            models.append( line.rstrip() )
    
    # Select a model
    model = userSelectModel(models) 

    # Function to send question to and recieve answer from OpenAI
    def onMessage(question):
        if isinstance(model, str) and isinstance(question, str):
            completion = openai.Completion.create(model=model, prompt=question)
            return completion.choices[0].text
        else:
            print("OpenAI requests must be strings")
            sys.exit(1)

    # While loop allowing ongoing conversation with OpenAI
    print("Type 'exit' or 'quit' to leave the chat.")
    while True:
        question = input("Ask a question > ")
        if question == "exit" or question == "quit":
            sys.exit(0)
        answer = onMessage(question)
        print(f"Bot: {answer}")

