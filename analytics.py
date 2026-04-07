from models import User, Transaction, Loan
from sqlalchemy import func

def get_analytics(db):

    users = db.session.query(func.count(User.id)).scalar()

    transactions = db.session.query(func.count(Transaction.id)).scalar()

    loans = db.session.query(func.count(Loan.id)).scalar()

    total_transfer = db.session.query(func.sum(Transaction.amount)).scalar()

    if total_transfer is None:
        total_transfer = 0

    return {
        "users":users,
        "transactions":transactions,
        "loans":loans,
        "transfer":total_transfer
    }