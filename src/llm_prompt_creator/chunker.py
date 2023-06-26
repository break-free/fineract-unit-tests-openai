from data_chunker import parser as JCParser
from data_chunker import java_code as JCChunker
import json
import os
import sys

"""
Comb for specified file types. Currently only works for java files (*.java)
Pulls out constants, constructors, fields, and methods and stores them as a Py dict in JSON file
"""
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("You must set an OPENAI_API_KEY environment variable value")
    
def chunker(directory, file_extension="*.java"):
    """Leverages data-chunker package to parse & chunk text-based code files into LLM-consumable tokens. Currently only supports java (*.java)"""
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
    with open('training_data.json', 'w') as f:
        json.dump(training_data_str, f)
    with open('chunks.json', 'w') as f:
        json.dump(chunks, f)
    with open('failed_files.json', 'w') as f:
        json.dump(failed_files, f)

