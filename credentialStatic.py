import ast

def flag_credential_exposure(parsed_ast):
    """
    Flags potential credential exposure vulnerabilities in the given Abstract Syntax Tree (AST).

    Args:
        parsed_ast (ast.AST): The Abstract Syntax Tree representation of a Python file.
    Returns:
        list: A list of flagged nodes that may indicate credential exposure vulnerabilities.    
    """

    flagged_nodes = []

    class CredentialExposureVisitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            for target in node.targets:

                if isinstance(target, ast.Name):
                    err_var = ["password", "passwd", "pwd", "secret", "token", "api_key", "access_key", "private_key", "apikey", "auth_key", "signing_key", "encryption_key"]
                    variable_name = target.id.lower()
                    if variable_name in err_var:
                        if isinstance(node.value, ast.Constant):
                            if type(node.value.value) in [str]:
                                flagged_nodes.append(f" {variable_name} = [REDACTED] at line {node.lineno}")
                            
                        # else:
                            # flagged_nodes.append(f" {variable_name} = [POTENTIAL CREDENTIAL EXPOSURE] at line {node.lineno}")

    scanner = CredentialExposureVisitor()
    scanner.visit(parsed_ast)

    return flagged_nodes