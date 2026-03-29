import re
import pandas as pd
import joblib
import os
from pycparser import c_parser
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "input_code.c")

parser = c_parser.CParser()
model = joblib.load("syntax_error_model.pkl")

KEYWORDS = [
    "int", "float", "char", "double", "return",
    "if", "else", "while", "for", "do",
    "break", "continue", "void", "switch", "case",
    "printf", "scanf"
]

# ---------------- TYPO DETECTION ----------------
def is_keyword_typo(code):

    lines = [line.strip() for line in code.split("\n") if line.strip()]

    if not lines:
        return False

    # check first line (function declaration)
    first_line = lines[0]

    if "(" in first_line:
        first_word = first_line.split()[0]

        if first_word not in KEYWORDS:
            for kw in KEYWORDS:
                if abs(len(first_word) - len(kw)) == 1:
                    diff = sum(1 for a, b in zip(first_word, kw) if a != b)
                    if diff == 1:
                        return True

    # check return typo
    for line in lines:
        words = line.split()

        if words:
            word = words[0]

            if word.startswith("r") and word != "return":
                if abs(len(word) - len("return")) <= 1:
                    diff = sum(1 for a, b in zip(word, "return") if a != b)
                    if diff == 1:
                        return True

    return False


# ---------------- SEMICOLON DETECTION ----------------
def is_missing_semicolon(code):

    lines = [line.strip() for line in code.split("\n") if line.strip()]

    for line in lines:

        if line.endswith("{") or line.endswith("}"):
            continue

        if line.startswith(("if", "for", "while", "else")):
            continue

        if "main(" in line:
            continue

        # 🔥 FIX: detect variable declarations also
        if not line.endswith(";"):
            if (
                "return" in line or
                "=" in line or
                "(" in line or
                ")" in line or
                line.startswith(("int", "float", "char", "double"))
            ):
                return True

    return False

# ---------------- ERROR LINE DETECTION ----------------
def get_error_line(code, error_msg):

    lines = [line for line in code.split("\n") if line.strip()]
    # 🔥 detect missing '{' after main
    if lines:
        first_line = lines[0].strip()
        if "main(" in first_line and "{" not in first_line:
            return 1

    # parser line
    match = re.search(r":(\d+):", error_msg)
    detected_line = int(match.group(1)) if match else None

    # 🔥 missing semicolon line
    for i, line in enumerate(lines):
      line_strip = line.strip()

      if not line_strip:
        continue

    # skip braces
      if line_strip.endswith("{") or line_strip.endswith("}"):
        continue

    # skip control headers
      if line_strip.startswith(("if", "for", "while", "else")):
        continue

      if "main(" in line_strip:
        continue

    # 🔥 NEW FIX: detect missing semicolon properly
    if not line_strip.endswith(";"):

        # if it's return OR assignment OR declaration
        if (
            line_strip.startswith("return") or
            "=" in line_strip or
            "(" in line_strip or
            any(line_strip.startswith(t) for t in ["int", "float", "char", "double"])
        ):
            return i + 1

    # 🔥 missing brace '}'
    open_braces = 0
    for i, line in enumerate(lines):
        open_braces += line.count("{")
        open_braces -= line.count("}")

        if open_braces < 0:
            return i + 1

    if open_braces > 0:
        return len(lines) + 1  # next line

    # fallback
    if detected_line:
        return detected_line

    return "Unknown"


# ---------------- FEATURE EXTRACTION ----------------
def extract_features(code):

    node_count = code.count(";")
    depth = code.count("{")
    if_count = code.count("if")
    line_count = code.count("\n")

    brace_diff = abs(code.count("{") - code.count("}"))
    paren_diff = abs(code.count("(") - code.count(")"))
    semicolon_count = code.count(";")

    return [
        node_count,
        depth,
        if_count,
        line_count,
        brace_diff,
        paren_diff,
        semicolon_count
    ]


columns = [
    "NodeCount",
    "TreeDepth",
    "IfCount",
    "LineCount",
    "BraceDifference",
    "ParenthesisDifference",
    "SemicolonCount"
]


# ---------------- MAIN CLASSIFIER ----------------
def classify_error(code):

    code = code.strip()

    try:
        parser.parse(code)
        print("No syntax error found.")
        return

    except Exception as e:
        error_msg = str(e).lower()

        features = extract_features(code)
        df = pd.DataFrame([features], columns=columns)

        prediction = model.predict(df)[0]

        # 🔥 RULE OVERRIDE (VERY IMPORTANT)

        if "expected ')'" in error_msg or abs(code.count("(") - code.count(")")) != 0:
            prediction = "MissingParenthesis"

        elif "expected '}'" in error_msg or abs(code.count("{") - code.count("}")) != 0:
            prediction = "MissingBrace"

        elif "expected ';'" in error_msg or is_missing_semicolon(code):
            prediction = "MissingSemicolon"

        elif is_keyword_typo(code):
            prediction = "KeywordTypo"

        else:
            prediction = "SyntaxError"

        diagnostics = {
            "MissingSemicolon": "Add ';' at end of statement.",
            "MissingBrace": "Check {} braces.",
            "MissingParenthesis": "Check () parentheses.",
            "SyntaxError": "Check syntax near error line.",
            "KeywordTypo": "Check misspelled keywords."
        }

        print("Predicted Error:", prediction)
        print("Error Line:", get_error_line(code, error_msg))
        print("Suggestion:", diagnostics[prediction])


# ---------------- TEST ----------------
code = r"""
int main() {
    int a;
    if (a > 5) 
        return 0
        }
}
"""
classify_error(code)