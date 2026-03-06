from pycparser import c_parser, c_ast
import os
import csv
import re

# -------- Locate input file --------
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "input_code.c")

# -------- Read C Code --------
with open(input_file, "r") as f:
    code = f.read()

parser = c_parser.CParser()

# -------- Initialize feature variables --------
node_count = 0
node_types = set()
if_count = 0
tree_depth = 0
error_line = 0
error_column = 0
label = "NoError"

# -------- Feature Extractor Class --------
class FeatureExtractor(c_ast.NodeVisitor):
    def __init__(self):
        self.node_count = 0
        self.node_types = set()
        self.if_count = 0

    def generic_visit(self, node):
        self.node_count += 1
        self.node_types.add(type(node).__name__)
        for c in node:
            self.visit(c)

    def visit_If(self, node):
        self.if_count += 1
        self.generic_visit(node)

# -------- Tree Depth Function --------
def calculate_depth(node):
    children = list(node)
    if not children:
        return 1
    return 1 + max(calculate_depth(child) for child in children)

# -------- Parsing and Feature Extraction --------
try:
    ast = parser.parse(code)

    extractor = FeatureExtractor()
    extractor.visit(ast)

    node_count = extractor.node_count
    node_types = extractor.node_types
    if_count = extractor.if_count
    tree_depth = calculate_depth(ast)

except Exception as e:
    label = "SyntaxError"
    
    # Extract line and column from error message
    match = re.search(r":(\d+):(\d+):", str(e))
    if match:
        error_line = int(match.group(1))
        error_column = int(match.group(2))

# -------- Convert to Feature Vector --------
feature_vector = [
    node_count,
    tree_depth,
    if_count,
    error_line,
    error_column,
    label
]

# -------- Save to CSV --------
output_file = os.path.join(current_dir, "ast_features.csv")

file_exists = os.path.isfile(output_file)

with open(output_file, "a", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # Write header only if file doesn't exist
    if not file_exists:
        writer.writerow([
            "NodeCount",
            "TreeDepth",
            "IfCount",
            "ErrorLine",
            "ErrorColumn",
            "Label"
        ])

    writer.writerow(feature_vector)

print("AST analysis completed. Features saved to ast_features.csv")