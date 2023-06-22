from data_chunker import parser
from data_chunker import java_code as JCC
import json
import os
import sys

if __name__ == '__main__':
    # Check that environment variables are set up.
    if "OPENAI_API_KEY" not in os.environ:
        print("You must set an OPENAI_API_KEY using the Secrets tool", file=sys.stderr)
    # Retrieve file list
    training_data = list()
    if len(sys.argv) != 3:
        print("2 command parameters required: (1) Enter one and only one absolute or relative path")
        print("to a directory containing the code to be chunked. (2) Enter the file extension for ")
        print("the files that need to be chunked. (e.g. python3 main.py training/test java)")
        exit()
    else:
        fileExtension = "*." + sys.argv[2]
        training_data = parser.get_file_list(sys.argv[1], fileExtension)
    # Chunk data using the files in the training data
    chunks = []
    failed_files = []

    if fileExtension == "*.java":
        for file in training_data:
            codelines = parser.get_code_lines(file)
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
    
    else:
        inputExtension = sys.argv[2]
        print(f'''File extension type "{inputExtension}" is currently not supported.''')
        exit()

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

