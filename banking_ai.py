from models import Transaction
from banking_knowledge import knowledge

def banking_ai(message, balance, user_id, db):
    msg = message.lower()

    transactions = Transaction.query.filter_by(user_id=user_id).all()

    # ---------------- GREETING ----------------
    if any(word in msg for word in ["hi", "hello", "hey"]):
        return "👋 Hello! I'm your Smart Banking Assistant."

    # ---------------- KNOWLEDGE BASE ----------------
    for key in knowledge:
        if key in msg:
            return f"📚 {knowledge[key]}"

    # ---------------- BALANCE ----------------
    if "balance" in msg:
        if balance < 1000:
            return f"💰 ₹{balance}\n⚠ Warning: Low balance!"
        elif balance > 50000:
            return f"💰 ₹{balance}\n💎 Great savings!"
        return f"💰 Your balance is ₹{balance}"

    # ---------------- TRANSACTIONS ----------------
    if "transaction" in msg or "history" in msg:
        if not transactions:
            return "📄 No transactions found."

        response = "📄 Recent transactions:\n"
        for t in transactions[-5:]:
            response += f"- {t.type}: ₹{t.amount}\n"

        return response

    # ---------------- SPENDING ----------------
    if "spend" in msg or "analysis" in msg:
        total_spent = sum(t.amount for t in transactions if t.type == "Transfer")

        if total_spent == 0:
            return "📊 No spending recorded."

        return f"📊 You spent ₹{total_spent}. Try to reduce unnecessary expenses."

    # ---------------- ADVICE ----------------
    if "advice" in msg or "suggest":
        if balance < 1000:
            return "⚠ Maintain minimum balance."

        return "💡 Try SIP, FD, or savings plan."

    # ---------------- LOAN ----------------
    if "loan" in msg:
        if balance < 2000:
            return "🏦 Loan approval chances are low."
        return "🏦 You are eligible for loan."

    return "🤖 Ask me anything about banking!"