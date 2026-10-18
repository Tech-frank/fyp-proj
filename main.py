from fileParser import parse_file_to_ast

file = input("Enter the path to the Python file: ")
try:
    parsed_ast = parse_file_to_ast(file)
    print("Successfully parsed the file into AST.")
    print(parsed_ast)
except Exception as e:
    print(f"Error parsing the file: {e}")
# Parse a Python file and get its AST
#parsed_ast = parse_file_to_ast('example.py')