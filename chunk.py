from java_code_chunker import chunker as JCC
import json, os, sys

if __name__ == '__main__':
    # Check that environment variables are set up.
    if "API_SECRET" not in os.environ:
        print("You must set an API_SECRET using the Secrets tool", file=sys.stderr)
    elif "OPENAI_API_KEY" not in os.environ:
        print("You must set an OPENAI_API_KEY using the Secrets tool", file=sys.stderr)
    # Retrieve file list
    training_data = list()
    if len(sys.argv) != 2 :
        print("Enter one and only one absolute or relative path to ")
        print("a directory containing the Java code to be chunked.")
    else:
        training_data = JCC.get_file_list(sys.argv[1], "*.java")
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
            # The `try` statements could be amalgamated but using them 
            # separately for now to get as many chunks as possible.
            try:
                chunks = chunks + JCC.chunk_constants(tree)
                chunks = chunks + JCC.chunk_constructors(tree, codelines)
                chunks = chunks + JCC.chunk_fields(tree, codelines)
                chunks = chunks + JCC.chunk_methods(tree, codelines)
            except JCC.ChunkingError as e:
                failed_files.append(str(file) + ": " + str(e))
        else:
            failed_files.append(str(file) + ", has no tree!")
    # Save each used list as a file for other operations.
    training_data_str = list()
    for data in training_data: # since Paths are not serializable
        training_data_str.append(str(data))
    with open('training_data.json', 'w') as f:
        json.dump(training_data_str, f)
    with open('chunks.json', 'w') as f:
        json.dump(chunks, f)
    with open('failed_files.json', 'w') as f:
        json.dump(failed_files, f)

