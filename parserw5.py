from pycparser import c_parser

# -------- INPUT: Single C program with syntax error --------
code = r"""
int main() {
    int a;
    if (a > 5) {
        return 0;
        }
}
"""
with open("input_code.c", "w") as c_file:
    c_file.write(code)
parser = c_parser.CParser()

# -------- OUTPUT FILES --------
error_file = open("syntax_errors.txt", "w")
ast_file = open("ast_output.txt", "w")

try:
    # Parse the C code
    ast = parser.parse(code)

    # If parsing succeeds, store AST
    ast_file.write("AST Generated Successfully\n")
    ast_file.write(str(ast))

    error_file.write("No syntax error detected\n")

except Exception as e:
    # If syntax error occurs, store error details
    error_file.write("Syntax Error Detected\n")
    error_file.write(str(e))
    ast_file.write("AST NOT GENERATED DUE TO SYNTAX ERROR\n")

# Close files
error_file.close()
ast_file.close()

print("Parsing completed. Check syntax_errors.txt and ast_output.txt")
