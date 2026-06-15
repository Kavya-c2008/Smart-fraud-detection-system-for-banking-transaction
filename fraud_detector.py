import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Load dataset
df = pd.read_csv("transactions.csv")

# Convert target
df["Status"] = df["Status"].map({"Normal": 0, "Fraud": 1})

# Features and target
X = df[["Amount", "OldBalance", "NewBalance"]]
y = df["Status"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Accuracy
# print("Model Accuracy:", model.score(X_test, y_test))
# print("Prediction:", predict_fraud(5000, 10000, 5000))

# CLEAN prediction (NO WARNING VERSION)
def predict_fraud(amount, old_balance, new_balance):

    input_data = pd.DataFrame(
        {
            "Amount": [amount],
            "OldBalance": [old_balance],
            "NewBalance": [new_balance]
        }
    )

    prediction = model.predict(input_data)[0]

    risk_score = model.predict_proba(input_data)[0][1] * 100

    if prediction == 1:
        return f"Fraud Transaction Detected | Risk Score: {risk_score:.2f}%"
    else:
        return f"Normal Transaction | Risk Score: {risk_score:.2f}%"
# Test
print("Prediction:", predict_fraud(5000, 10000, 5000))