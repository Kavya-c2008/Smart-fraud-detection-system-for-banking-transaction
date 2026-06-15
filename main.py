from reportlab.pdfgen import canvas
from flask import send_file
from flask import Flask, render_template, request, redirect, session
from fraud_detector import predict_fraud
import pandas as pd
import matplotlib.pyplot as plt
import csv

app = Flask(__name__)
app.secret_key = "fraudproject"

# ---------------- LOGIN ----------------

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():

    username = request.form['username']
    password = request.form['password']

    with open('users.csv', 'r') as file:
        reader = csv.reader(file)

        next(reader)

        for row in reader:
            if row[0] == username and row[1] == password:
                session['user'] = username
                return redirect('/')

    return "Invalid Username or Password"


# ---------------- REGISTER ----------------

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register_post():

    username = request.form['username']
    password = request.form['password']

    with open('users.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, password])

    return redirect('/login')


# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# ---------------- HOME ----------------

@app.route('/')
def home():

    if 'user' not in session:
        return redirect('/login')

    return render_template('index.html')


# ---------------- PREDICT ----------------

@app.route('/predict', methods=['POST'])
def predict():

    amount = float(request.form['amount'])
    old_balance = float(request.form['oldbalance'])
    new_balance = float(request.form['newbalance'])

    result = predict_fraud(
        amount,
        old_balance,
        new_balance
    )

    return render_template(
        'index.html',
        result=result
    )


# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    history = pd.read_csv("history.csv")

    total = len(history)

    fraud = len(
        history[
            history["Result"] ==
            "Fraud Transaction Detected"
        ]
    )

    normal = total - fraud

    plt.figure(figsize=(5, 5))

    plt.pie(
        [fraud, normal],
        labels=["Fraud", "Normal"],
        autopct="%1.1f%%"
    )

    plt.savefig("static/fraud_chart.png")
    plt.close()

    return render_template(
        "dashboard.html",
        total=total,
        fraud=fraud,
        normal=normal
    )
@app.route('/download_report')
def download_report():

    pdf_file = "Fraud_Report.pdf"

    pdf = canvas.Canvas(pdf_file)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 800, "Smart Fraud Detection Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 760, "Generated Successfully")

    pdf.save()

    return send_file(
        pdf_file,
        as_attachment=True
    )
@app.route('/admin')
def admin():

    users_df = pd.read_csv("users.csv")
    history_df = pd.read_csv("history.csv")

    users = len(users_df)
    transactions = len(history_df)

    frauds = len(
        history_df[
            history_df["Result"]
            .astype(str)
            .str.contains("Fraud", case=False)
        ]
    )

    return render_template(
        "admin.html",
        users=users,
        transactions=transactions,
        frauds=frauds
    )
@app.route('/history')
def history():

    history_df = pd.read_csv("history.csv")

    search = request.args.get('search')

    if search:

        history_df = history_df[
            history_df["Amount"]
            .astype(str)
            .str.contains(search)
        ]

    records = history_df.to_dict(
        orient='records'
    )

    return render_template(
        'history.html',
        records=records
    )

if __name__ == "__main__":
    app.run(debug=True)
