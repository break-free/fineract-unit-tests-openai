import json 
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
    num_member_tokens = 0
    num_method_tokens = 0
    max_tokens = 0
    num_member_chunks = len(chunks)
    num_method_chunks = 0
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

if __name__ == '__main__':
    # Load the files containing the data
    with open('training_data.json', 'r') as f:
        training_data = json.load(f)
    with open('chunks.json', 'r') as f:
        chunks = json.load(f)
    with open('failed_files.json', 'r') as f:
        failed_files = json.load(f)
    # Print parsing and token statistics
    print_parsing_statistics(training_data, failed_files)
    print_token_statistics(chunks)
#    print_chunks_sample(chunks)
