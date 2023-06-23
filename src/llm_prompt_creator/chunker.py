from java_code_chunker import chunker as JCC
import json
import os
import sys

"""
Comb for specified file types. Currently only works for java files (*.java)
Pulls out constants, constructors, fields, and methods and stores them as a Py dict in JSON file
"""
if "OPENAI_API_KEY" not in os.environ:
    print("You must set an OPENAI_API_KEY environment variable value", file=sys.stderr)
    
def chunker(directory, file_extension="*.java"):
    training_data = list()
    # if directory == None:
    #     print("Must provide an input directory to chunk into tokens")
    
    training_data = JCC.get_file_list(directory, file_extension=file_extension)
    # Chunk data using the files in the training data
    chunks = []
    failed_files = []
    for file in training_data:
        codelines = JCC.get_code_lines(file)
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
    
    # Convert training_data paths into strings for serialization.
    training_data_str = list()
    for data in training_data: 
        training_data_str.append(str(data))
    # Save each used list as a file for other operations.
    with open('training_data.json', 'w') as f:
        json.dump(training_data_str, f)
    with open('chunks.json', 'w') as f:
        json.dump(chunks, f)
    with open('failed_files.json', 'w') as f:
        json.dump(failed_files, f)

