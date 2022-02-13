from server.database import db
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

class Transaction(db.Model):
    __tablename__ = "transactions"

    transactionId = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    merchantId = db.Column(UUID(as_uuid=True), db.ForeignKey('merchants.merchantId'), default=uuid4, nullable=False)
    incomeAccount = db.Column(UUID(as_uuid=True), db.ForeignKey('accounts.accountId'), default=uuid4, nullable=False)
    outcomeAccount = db.Column(UUID(as_uuid=True), db.ForeignKey('accounts.accountId'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    extraData = db.Column(db.String(255))
    signature = db.Column(db.String(255))
    status = db.Column(db.Enum("INITIALIZED", "CONFIRMED", "VERIFIED", "COMPLETED", "CANCELED", "EXPIRED", "FAILED", 
                        name="transaction_status", create_type=False), nullable=False)

    def __init__(self, merchantId, incomeAccount, outcomeAccount, amount, extraData, signature):
        self.merchantId = merchantId
        self.incomeAccount = incomeAccount
        self.outcomeAccount = outcomeAccount
        self.amount = amount
        self.extraData = extraData
        self.signature = signature
        self.status = "INITIALIZED"

    def update_status(self, status):
        self.status = status

    def confirm_outcomeAccount(self, outcomeAccount):
        self.outcomeAccount = outcomeAccount

    def check_confirmation(self, balance):
        if balance > self.amount:
            return True
        return False