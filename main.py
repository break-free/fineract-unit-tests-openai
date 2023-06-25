#!/usr/bin/env python3

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
    # Create positional and optional command arguments
    parser = argparse.ArgumentParser(description='Create a vector store to pass contextual data to an LLM prompt')
    parser.add_argument('data_path', help='the location of the training data', default=None)
    parser.add_argument('file_extension', help='the file extension to be searched for and then parsed, e.g., *.java', default=None)
    parser.add_argument('-d', '--dump-files', action='store_true', dest='dump_key_files', help='dump key info into files', default=False)
    parser.add_argument('-f', '--parse-files', action='store', dest='parse_files', help='one or more files that contain prompt questions', nargs='*')
    parser.add_argument('-p', '--master-prompt', action='store', dest='master_prompt', help='master prompt path, default is `training/master.prompt`', default='training/master.prompt')
    parser.add_argument('-c', '--show-context', action='store_true', dest='show_context', help='show the context passed to the LLM', default=False)
    parser.add_argument('-s', '--show-statistics', action='store_true', dest='show_statistics', help='show the parsing and chunking statistics', default=False)
    args = parser.parse_args()

    data, chunks, failed_files = p.chunk(args.data_path, args.file_extension)
    if args.show_statistics:
        p.print_parsing_statistics(data, failed_files)
        p.print_token_statistics(chunks)
    if args.dump_key_files:
        dump_key_files(data, chunks, failes_files)
    store = p.train(chunks)
    if args.parse_files == None:
        p.prompter(store, args.master_prompt, args.show_context)
    else:
        p.files_prompter(store, args.master_prompt, args.show_context)
