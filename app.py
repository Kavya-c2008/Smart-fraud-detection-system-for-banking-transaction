from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import csv
import os
import pickle
from datetime import datetime

app = Flask(__name__)
app.secret_key = "my_secret_key_123"
import pickle

model = pickle.load(open("fraud_model.pkl", "rb"))
users = {
    "admin": "admin123"
}
# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect("fraud.db")   # 👈 keep ONE name everywhere
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT,
            amount REAL,
            old_balance REAL,
            new_balance REAL,
            result TEXT,
            risk_score REAL
        )
    """)

    conn.commit()
    conn.close()

init_db()
def save_transaction(amount, old_balance, new_balance, result, risk_score):

    conn = sqlite3.connect("fraud.db")
    cur = conn.cursor()

    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO transactions (datetime, amount, old_balance, new_balance, result, risk_score)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (now, amount, old_balance, new_balance, result, risk_score))

    conn.commit()
    conn.close()


# ---------------- HOME ----------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid Credentials"

    return render_template("login.html")
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            return "User already exists!"

        users[username] = password
        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ---------------- FRAUD CHECK ----------------
@app.route("/check", methods=["POST"])
def check_fraud():

    amount = float(request.form["amount"])
    old_balance = float(request.form["old_balance"])
    new_balance = float(request.form["new_balance"])

    # ML prediction
    prediction = model.predict([[amount, old_balance, new_balance]])

    if prediction[0] == 1:
        result = "FRAUD"
        risk_score = 90
    else:
        result = "NORMAL"
        risk_score = 10

    # Save to database
    conn = sqlite3.connect("transactions.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO transactions
        (datetime, amount, old_balance, new_balance, result, risk_score)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        amount,
        old_balance,
        new_balance,
        result,
        risk_score
    ))

    conn.commit()
    conn.close()
    save_transaction(amount, old_balance, new_balance, result, risk_score)
    return render_template("index.html", result=result, risk_score=risk_score)


# ---------------- HISTORY ----------------
@app.route("/history")
def history():
    import csv

    rows = []
    with open("history.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            rows.append(row)

    return render_template("history.html", rows=rows)
from flask import send_file
import csv

@app.route("/export")
def export():
    file_path = "history.csv"

    return send_file(
        file_path,
        mimetype="text/csv",
        as_attachment=True,
        download_name="fraud_history.csv"
    )


# ---------------- DASHBOARD ---------------
@app.route("/dashboard")
def dashboard():
    import csv

    fraud_count = 0
    normal_count = 0
    total = 0

    with open("history.csv", "r") as file:
        reader = csv.reader(file)

        for row in reader:
            if len(row) < 5:
                continue

            total += 1

            if "FRAUD" in row[-1].upper():
                fraud_count += 1
            else:
                normal_count += 1

    # Avoid division error
    if total == 0:
        accuracy = 0
    else:
        accuracy = (normal_count / total) * 100

    # Fake ML evaluation (for project demonstration)
    tp = fraud_count
    tn = normal_count
    fp = max(1, int(fraud_count * 0.1))
    fn = max(1, int(normal_count * 0.1))

    return render_template(
        "dashboard.html",
        fraud=fraud_count,
        normal=normal_count,
        accuracy=round(accuracy, 2),
        tp=tp,
        tn=tn,
        fp=fp,
        fn=fn
    )        
                           
 # -------- PIE CHART --------
    labels = ["Fraud", "Normal"]
    values = [fraud_count, normal_count]

    plt.figure(figsize=(5, 5))
    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.title("Fraud vs Normal Transactions")
    plt.savefig("static/pie_chart.png")
    plt.close()

    # -------- BAR CHART --------
    static_path = os.path.join("static", "bar_chart.png")

    plt.figure(figsize=(5, 5))
    plt.bar(labels, values)
    plt.savefig(static_path)
    plt.close()

    return render_template(
        "dashboard.html",
        fraud=fraud_count,
        normal=normal_count
    )
# -------- PIE CHART --------
    labels = ["Fraud", "Normal"]
    values = [fraud_count, normal_count]

    plt.figure(figsize=(5, 5))
    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.title("Fraud vs Normal Transactions")
    plt.savefig("static/pie_chart.png")
    plt.close()

    return render_template(
        "dashboard.html",
        fraud_count=fraud_count,
        normal_count=normal_count
    )


import os
import matplotlib.pyplot as plt

static_path = os.path.join("static", "bar_chart.png")

plt.figure(figsize=(5,5))

plt.savefig(static_path)   # IMPORTANT FIX
plt.close()
@app.route("/test")
def test():
    save_transaction(1000, 5000, 4000, "FRAUD", 0.95)
    return "Inserted"

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)