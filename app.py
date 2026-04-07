from flask import Flask, render_template, request, redirect, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from config import Config
from models import db, User, Transaction, Loan
from banking_ai import banking_ai
from fraud_detection import detect_fraud

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect("/dashboard")
    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        existing = User.query.filter_by(username=request.form["username"]).first()
        if existing:
            return "⚠ Username already exists!"

        role = "admin" if User.query.count()==0 else "user"

        user = User(
            username=request.form["username"],
            password=generate_password_hash(request.form["password"]),
            role=role
        )

        db.session.add(user)
        db.session.commit()
        return redirect("/")

    return render_template("register.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
@login_required
def dashboard():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    monthly_data = {}

    for t in transactions:
        month = datetime.now().strftime("%b")
        if t.type == "Transfer":
            monthly_data[month] = monthly_data.get(month, 0) + t.amount

    months = list(monthly_data.keys())
    amounts = list(monthly_data.values())

    return render_template(
        "dashboard.html",
        user=current_user,
        transactions=transactions,
        months=months,
        amounts=amounts
    )

# ---------------- DEPOSIT ----------------
@app.route("/deposit", methods=["POST"])
@login_required
def deposit():
    amount = float(request.form["amount"])
    current_user.balance += amount

    t = Transaction(type="Deposit", amount=amount, user_id=current_user.id)
    db.session.add(t)
    db.session.commit()

    return redirect("/dashboard")

# ---------------- TRANSFER ----------------
@app.route("/transfer", methods=["POST"])
@login_required
def transfer():
    receiver = User.query.filter_by(username=request.form["receiver"]).first()
    amount = float(request.form["amount"])

    fraud = detect_fraud(current_user, amount)
    if fraud != "Safe":
        return f"<h2>{fraud}</h2><a href='/dashboard'>Go Back</a>"

    if receiver and current_user.balance >= amount:
        current_user.balance -= amount
        receiver.balance += amount

        t = Transaction(type="Transfer", amount=amount, user_id=current_user.id)
        db.session.add(t)
        db.session.commit()

    return redirect("/dashboard")

# ---------------- APPLY LOAN ----------------
@app.route("/apply_loan", methods=["POST"])
@login_required
def apply_loan():
    amount = float(request.form["amount"])
    reason = request.form["reason"]

    loan = Loan(
        user_id=current_user.id,
        amount=amount,
        reason=reason,
        status="Pending"
    )

    db.session.add(loan)
    db.session.commit()

    return redirect("/dashboard")

# ---------------- APPROVE LOAN ----------------
@app.route("/approve_loan/<int:loan_id>")
@login_required
def approve_loan(loan_id):
    if current_user.role != "admin":
        return "Access Denied"

    loan = Loan.query.get(loan_id)

    if loan and loan.status == "Pending":
        loan.status = "Approved"

        user = User.query.get(loan.user_id)
        user.balance += loan.amount

        db.session.commit()

    return redirect("/admin")

# ---------------- REJECT LOAN ----------------
@app.route("/reject_loan/<int:loan_id>")
@login_required
def reject_loan(loan_id):
    if current_user.role != "admin":
        return "Access Denied"

    loan = Loan.query.get(loan_id)

    if loan and loan.status == "Pending":
        loan.status = "Rejected"
        db.session.commit()

    return redirect("/admin")

# ---------------- CHAT ----------------
@app.route("/chat", methods=["POST"])
@login_required
def chat():
    msg = request.json["message"]
    answer = banking_ai(msg, current_user.balance, current_user.id, db)
    return jsonify({"answer": answer})

# ---------------- ADMIN ----------------
@app.route("/admin")
@login_required
def admin():
    if current_user.role != "admin":
        return "Access Denied"

    users = User.query.all()
    loans = Loan.query.all()

    total_users = len(users)
    total_balance = sum(u.balance for u in users)

    return render_template(
        "admin.html",
        users=users,
        loans=loans,
        total_users=total_users,
        total_balance=total_balance
    )

# ---------------- LOGOUT ----------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)