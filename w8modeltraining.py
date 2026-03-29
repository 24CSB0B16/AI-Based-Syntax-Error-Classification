from w7dataset import generate_dataset
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, classification_report
import joblib

data = generate_dataset()

X = data.drop("ErrorLabel", axis=1)
y = data["ErrorLabel"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

model = RandomForestClassifier(
    n_estimators=300,
    class_weight='balanced',
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred, average='weighted', zero_division=0))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred, zero_division=0))

joblib.dump(model, "syntax_error_model.pkl")
print("Model saved.")