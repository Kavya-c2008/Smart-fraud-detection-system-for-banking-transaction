import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle

data = {
    "amount": [500, 2000, 15000, 300, 20000, 700, 12000, 400],
    "old_balance": [10000, 8000, 50000, 12000, 60000, 9000, 45000, 7000],
    "new_balance": [9500, 6000, 35000, 11700, 40000, 8500, 30000, 6500],
    "label": [0, 0, 1, 0, 1, 0, 1, 0]
}

df = pd.DataFrame(data)

X = df[["amount", "old_balance", "new_balance"]]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LogisticRegression()
model.fit(X_train, y_train)

# IMPORTANT: correct saving
with open("fraud_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model created successfully")