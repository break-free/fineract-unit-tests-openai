import argparse
import json
import os
import prompter as p
import sys

def dump_files(data:list, chunks:list, failed_files:list):

    # Convert training_data paths into strings for serialization.
    data_str = list()
    for d in data: 
        data_str.append(str(d))
    # Save each used list as a file for other operations.
    with open('training_data.json', 'w') as f:
        json.dump(data_str, f)
    with open('chunks.json', 'w') as f:
        json.dump(chunks, f)
    with open('failed_files.json', 'w') as f:
        json.dump(failed_files, f)

if __name__ == "__main__":

    # Check that environment variables are set up.
    if "OPENAI_API_KEY" not in os.environ:
        print("You must set an OPENAI_API_KEY using the Secrets tool", file=sys.stderr)

    parser = argparse.ArgumentParser()
    parser.add_argument('--training-data', dest='training_data_path', default=None)
    parser.add_argument('--file-extension', dest='file_extension', default=None)
    args = parser.parse_args()
    # Check that environment variables are set up.
    if args.training_data_path == None or args.file_extension == None:
        print("2 command parameters required: (1) Enter one and only one absolute or relative path")
        print("to a directory containing the code to be chunked. (2) Enter the file extension for ")
        print("the files that need to be chunked. (e.g. python3 main.py training/test *.java)")
        exit()
    data, chunks, failed_files = p.chunk(args.training_data_path, 
                                                         args.file_extension)

    p.print_parsing_statistics(data, failed_files)
    p.print_token_statistics(chunks)
    store = p.train(chunks)
    p.prompter(store)

