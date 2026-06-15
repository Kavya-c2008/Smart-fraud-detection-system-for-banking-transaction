from sklearn.metrics import accuracy_score
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

data = pd.read_csv("transactions.csv")

# Convert labels to numbers
data["Status"] = data["Status"].map({
    "Normal": 0,
    "Fraud": 1
})

X = data[["Amount"]]
y = data["Status"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = DecisionTreeClassifier()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("Model Accuracy:", accuracy * 100, "%")

amount = pd.DataFrame({"Amount": [180000]})

prediction = model.predict(amount)

if prediction[0] == 1:
    print("Fraud Transaction Detected")
else:
    print("Normal Transaction")