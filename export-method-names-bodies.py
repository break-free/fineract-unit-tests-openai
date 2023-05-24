import javalang
from pathlib import Path

def get_method_start_end(method_node):
    startpos  = None
    endpos    = None
    startline = None
    endline   = None
    for path, node in tree:
        if startpos is not None and method_node not in path:
            endpos = node.position
            endline = node.position.line if node.position is not None else None
            break
        if startpos is None and node == method_node:
            startpos = node.position
            startline = node.position.line if node.position is not None else None
    return startpos, endpos, startline, endline

def get_method_text(startpos, endpos, startline, endline, last_endline_index):
    if startpos is None:
        return "", None, None, None
    else:
        startline_index = startline - 1 
        endline_index = endline - 1 if endpos is not None else None 

        # 1. check for and fetch annotations
        if last_endline_index is not None:
            for line in codelines[(last_endline_index + 1):(startline_index)]:
                if "@" in line: 
                    startline_index = startline_index - 1
        meth_text = "<ST>".join(codelines[startline_index:endline_index])
        meth_text = meth_text[:meth_text.rfind("}") + 1] 

        # 2. remove trailing rbrace for last methods & any external content/comments
        # if endpos is None and 
        if not abs(meth_text.count("}") - meth_text.count("{")) == 0:
            # imbalanced braces
            brace_diff = abs(meth_text.count("}") - meth_text.count("{"))

            for _ in range(brace_diff):
                meth_text  = meth_text[:meth_text.rfind("}")]    
                meth_text  = meth_text[:meth_text.rfind("}") + 1]     

        meth_lines = meth_text.split("<ST>")  
        meth_text  = "".join(meth_lines)                   
        last_endline_index = startline_index + (len(meth_lines) - 1) 

        return meth_text, (startline_index + 1), (last_endline_index + 1), last_endline_index

if __name__ == "__main__":
    trainingData = list(Path("training/facts/").glob("**/*.java"))

    if len(trainingData) < 1:
        print("The folder training/facts should be populated with at least one .java file", file=sys.stderr)

    for training in trainingData:

        with open(training, 'r') as r:
            codelines = r.readlines()
            code_text = ''.join(codelines)

        lex = None
        try:
            tree = javalang.parse.parse(code_text)
        except javalang.parser.JavaSyntaxError as e:
            continue
        methods = {}
        for _, method_node in tree.filter(javalang.tree.MethodDeclaration):
            startpos, endpos, startline, endline = get_method_start_end(method_node)
            method_text, startline, endline, lex = get_method_text(startpos, endpos, startline, endline, lex)
            methods[method_node.name] = method_text

            if "@Test" in method_text:
                print(method_node.name)
#                print(method_text)

