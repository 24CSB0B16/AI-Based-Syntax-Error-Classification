import os
import pandas as pd
from pycparser import c_parser, c_ast

INPUT_FOLDER = "input_programs"
parser = c_parser.CParser()

# ---------------- Feature Extractor ----------------

class FeatureExtractor(c_ast.NodeVisitor):

    def __init__(self):
        self.node_count = 0
        self.if_count = 0

    def generic_visit(self, node):
        self.node_count += 1
        for c in node:
            self.visit(c)

    def visit_If(self, node):
        self.if_count += 1
        self.generic_visit(node)


def tree_depth(node):
    children = list(node)
    if not children:
        return 1
    return 1 + max(tree_depth(c) for c in children)


# ---------------- DATASET FUNCTION ----------------

def generate_dataset():

    rows = []

    for fname in os.listdir(INPUT_FOLDER):

        if not fname.endswith(".c"):
            continue

        path = os.path.join(INPUT_FOLDER, fname)

        with open(path, "r") as f:
            code = f.read()

        # ----------- NEW FEATURES (always compute) -----------
        line_count = code.count("\n")
        brace_diff = abs(code.count("{") - code.count("}"))
        paren_diff = abs(code.count("(") - code.count(")"))
        semicolon_count = code.count(";")

        try:
            ast = parser.parse(code)

            extractor = FeatureExtractor()
            extractor.visit(ast)

            node_count = extractor.node_count
            if_count = extractor.if_count
            depth = tree_depth(ast)

            error_label = "NoError"

        except Exception as e:

            node_count = 0
            if_count = 0
            depth = 0

            msg = str(e).lower()

            if brace_diff != 0:
                error_label = "MissingBrace"

            elif paren_diff != 0:
                error_label = "MissingParenthesis"

            elif "expected ';'" in msg:
                error_label = "MissingSemicolon"

            else:
                error_label = "SyntaxError"

        rows.append([
            node_count,
            depth,
            if_count,
            line_count,
            brace_diff,
            paren_diff,
            semicolon_count,
            error_label
        ])

    df = pd.DataFrame(rows, columns=[
        "NodeCount",
        "TreeDepth",
        "IfCount",
        "LineCount",
        "BraceDifference",
        "ParenthesisDifference",
        "SemicolonCount",
        "ErrorLabel"
    ])

    df.to_csv("syntax_error_dataset.csv", index=False)

    print("Improved dataset generated successfully.")

    return df

# Only runs if executed directly (not when imported)
if __name__ == "__main__":
    generate_dataset()