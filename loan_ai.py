def check_loan_eligibility(balance, amount):

    if balance < 1000:
        return "Rejected"

    if amount > balance * 5:
        return "Rejected"

    if amount < 5000:
        return "Approved"

    if amount < 50000:
        return "Approved"

    return "Pending"