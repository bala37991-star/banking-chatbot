def detect_fraud(user, amount):

    if amount > 50000:
        return "⚠ Suspicious: Large transaction"

    if amount > user.balance * 2:
        return "⚠ Suspicious: Unusual transaction"

    return "Safe"