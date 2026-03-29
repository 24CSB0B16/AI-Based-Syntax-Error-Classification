import re
import pandas as pd
import joblib
from pycparser import c_parser

parser = c_parser.CParser()
model = joblib.load("syntax_error_model.pkl")

KEYWORDS = [
    "int", "float", "char", "double", "return",
    "if", "else", "while", "for", "do",
    "break", "continue", "void", "switch", "case",
    "printf", "scanf"
]

SECURITY_MAP = {
    "MissingSemicolon": {
        "risk": "Statement truncation / unintended execution",
        "severity": "Low"
    },
    "MissingBrace": {
        "risk": "Control flow manipulation",
        "severity": "High"
    },
    "MissingParenthesis": {
        "risk": "Incorrect condition evaluation",
        "severity": "Medium"
    },
    "KeywordTypo": {
        "risk": "Invalid or unintended behavior",
        "severity": "Medium"
    },
    "SyntaxError": {
        "risk": "Compilation failure / undefined behavior",
        "severity": "Low"
    }
}


# ---------------- TYPO DETECTION ----------------
def is_keyword_typo(code):
    lines = [line.strip() for line in code.split("\n") if line.strip()]

    if not lines:
        return False

    first_line = lines[0]

    if "(" in first_line:
        first_word = first_line.split()[0]

        if first_word not in KEYWORDS:
            for kw in KEYWORDS:
                if abs(len(first_word) - len(kw)) == 1:
                    diff = sum(1 for a, b in zip(first_word, kw) if a != b)
                    if diff == 1:
                        return True

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

        if not line.endswith(";"):
            if (
                "return" in line or
                "=" in line or
                "(" in line or
                ")" in line or
                any(line.startswith(t) for t in ["int", "float", "char", "double"])
            ):
                return True

    return False


# ---------------- ERROR LINE DETECTION ----------------
def get_error_line(code, error_msg):
    lines = [line for line in code.split("\n") if line.strip()]

    # missing '{'
    if lines:
        if "main(" in lines[0] and "{" not in lines[0]:
            return 1

    # 🔥 FIXED LOOP (correct indentation)
    for i, line in enumerate(lines):
        line_strip = line.strip()

        if not line_strip:
            continue

        if line_strip.endswith("{") or line_strip.endswith("}"):
            continue

        if line_strip.startswith(("if", "for", "while", "else")):
            continue

        if "main(" in line_strip:
            continue

        if not line_strip.endswith(";"):
            if (
                line_strip.startswith("return") or
                "=" in line_strip or
                "(" in line_strip or
                any(line_strip.startswith(t) for t in ["int", "float", "char", "double"])
            ):
                return i + 1

    # brace mismatch
    open_braces = 0
    for i, line in enumerate(lines):
        open_braces += line.count("{")
        open_braces -= line.count("}")

        if open_braces < 0:
            return i + 1

    if open_braces > 0:
        return len(lines) + 1

    # fallback
    match = re.search(r":(\d+):", error_msg)
    if match:
        return int(match.group(1))

    return "Unknown"


# ---------------- FEATURE EXTRACTION ----------------
def extract_features(code):
    return [
        code.count(";"),
        code.count("{"),
        code.count("if"),
        code.count("\n"),
        abs(code.count("{") - code.count("}")),
        abs(code.count("(") - code.count(")")),
        code.count(";")
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

    prediction = "NoError"

    try:
        parser.parse(code)

        print("No syntax error found.")

        security = {
            "risk": "None",
            "severity": "None"
        }

        print("Security Risk:", security["risk"])
        print("Severity Level:", security["severity"])

        return

    except Exception as e:
        error_msg = str(e).lower()

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

        security = SECURITY_MAP.get(prediction, {
            "risk": "Unknown",
            "severity": "Unknown"
        })

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
        print("Security Risk:", security["risk"])
        print("Severity Level:", security["severity"])


# ---------------- TEST ----------------
code = r"""
int main() {
    int a=5;
    print(a)
    return 0;
}
"""

classify_error(code)
