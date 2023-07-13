#!/usr/bin/env python3

import argparse
import json
import os
import pickle
import prompter as p
import sys

def dump_key_files(data:list, chunks:list, failed_files:list):

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
    parser.add_argument('-c', '--show-context', action='store_true', dest='show_context', help='Show the context passed to the LLM.', default=False)
    parser.add_argument('-d', '--dump-files', action='store_true', dest='dump_key_files', help='Dump data files, chunks, file parsing errors and resultant vector store into files. Note that a prompt will not be loaded on completiong.', default=False)
    parser.add_argument('-f', '--parse-files', action='append', dest='parse_files', help='One or more files that contain prompt questions.')
    parser.add_argument('-l', '--load-store', action='store_true', dest='vectorstore', help='Tells the parser to use an existing store `store.pkl` and training index `training.index`.', default=False)
    parser.add_argument('-p', '--master-prompt', action='store', dest='master_prompt', help='Master prompt path, default is `training/master.prompt`.', default='training/master.prompt')
    parser.add_argument('-s', '--show-statistics', action='store_true', dest='show_statistics', help='Show the parsing and chunking statistics.', default=False)
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='Show the additional information.', default=False)
    parser.add_argument('data_path', help='The location of the training data.', default=None, nargs='?')
    parser.add_argument('file_extension', help='The file extension to be searched for and then parsed, e.g., *.java.', default=None, nargs='?')
    args = parser.parse_args()
    if not args.data_path or not args.file_extension:
        if not args.vectorstore:
            parser.print_help()
            sys.exit()

    chunks = []
    if not args.vectorstore:
        data, chunks, failed_files = p.chunk(args.data_path, args.file_extension, args.verbose)
        if args.show_statistics:
            p.print_parsing_statistics(data, failed_files)
            p.print_token_statistics(chunks)
        if args.dump_key_files:
            dump_key_files(data, chunks, failed_files)

    store = None
    if args.vectorstore:
        print("Loading store ...")
        try:
            with open("store.pkl", "rb") as f:
                store = pickle.load(f)
        except FileNotFoundError as e:
            print("File `store.pkl` not found. Remove the `-l` or " +
                  "`--load-store` switch from the `demo.py` command.")
            sys.exit(1)
    else:
        store = p.train(chunks)
        if args.dump_key_files:
            with open("store.pkl", "wb") as f:
                pickle.dump(store, f)

    if not args.dump_key_files:
        if args.parse_files == None:
            p.prompter(store, args.master_prompt, args.show_context)
        else:
            p.files_prompter(store, args.master_prompt, args.parse_files, args.show_context)
