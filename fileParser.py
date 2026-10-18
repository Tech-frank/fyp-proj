import ast

def parse_file_to_ast(file):
    """
    Parses a Python file and returns its Abstract Syntax Tree (AST).

    Args:
        file (str): The path to the Python file to be parsed.

    Returns:
        ast.AST: The Abstract Syntax Tree representation of the Python file.
        """

    with open(file, 'r', encoding='utf-8') as f:
        file_content = f.read()

    # Parse the file content into an AST
        return ast.parse(file_content, filename=file)
