#  AI-Based Syntax Error Classifier 

##  Overview

This project is a Compiler Design (CD) project that uses Machine Learning to detect and classify syntax errors in C programs.

It processes input C code, extracts features using AST (Abstract Syntax Tree), and predicts the type of syntax error along with its location and possible fix.

---

##  Objectives

* Automate syntax error detection in C programs
* Classify errors using ML models
* Provide meaningful suggestions for correction
* Reduce manual debugging effort

---

## Tech Stack

* **Language:** Python
* **Concepts:** Compiler Design, AST (Abstract Syntax Tree)
* **Machine Learning:** Classification model (trained using dataset)
* **Libraries:** (mention if used: sklearn, pandas, etc.)

---

##  Project Structure

```bash
/project-folder
│── README.md                  # Project documentation
│
│── input_code.c              # Sample input C program
│── syntax_errors.txt         # List of known syntax errors
│
│── syntax_error_dataset.csv  # Dataset used for training
│── ast_features.csv          # Extracted AST features
│
│── ast_output.txt            # AST representation of input code
│
│── parserw5.py               # Parses C code and generates AST
│── w6ast.py                  # AST feature extraction logic
│── w7dataset.py              # Dataset preparation and preprocessing
│── w8modeltraining.py        # ML model training script
│── week9.py                  # Final integration / prediction script
│
│── syntax_error_model.pkl    # Trained ML model
```

---

##  Workflow

1. **Input Code**

   * User provides C code (`input_code.c`)

2. **Parsing**

   * `parserw5.py` generates AST from input code

3. **Feature Extraction**

   * `w6ast.py` extracts relevant features from AST
   * Stored in `ast_features.csv`

4. **Dataset Preparation**

   * `w7dataset.py` processes and prepares training dataset

5. **Model Training**

   * `w8modeltraining.py` trains ML model
   * Model saved as `syntax_error_model.pkl`

6. **Prediction**

   * `week9.py` loads model and predicts:

     * Error Type
     * Error Line
     * Suggestion

---

## How to Run

### Step 1: Clone Repository

```bash
git clone https://github.com/24CSB0B16/AI-Based-Syntax-Error-Classification.git
cd AI-Based-Syntax-Error-Classification
```

### Step 2: Run Full Pipeline

```bash
python parserw5.py
python w6ast.py
python w7dataset.py
python w8modeltraining.py
python week9.py
```

---

##  Example

### Input (`input_code.c`)

```c
int main() {
    int a = 5
    printf("%d", a);
}
```

### Output

```
Predicted Error: MissingSemicolon
Error Line: 2
Suggestion: Add ';' at end of statement
```

---

##  Dataset Details

* Contains labeled syntax errors
* Includes error type, code snippet, and features
* Used to train classification model

---

## Future Improvements

* Support multiple programming languages
* Improve accuracy using deep learning models
* Add real-time error detection
* Develop web-based interface

---

##  Author
Ch Geetha Vandhana
---

##  License

This project is licensed under the MIT License.

