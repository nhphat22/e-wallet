from sqlalchemy import ForeignKey
from server.database import db
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

class Merchant(db.Model):
    __tablename__ = "merchants"

    merchantId = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    accountId = db.Column(UUID(as_uuid=True), db.ForeignKey('accounts.accountId'), default=uuid4, nullable=False)
    merchantName = db.Column(db.String(200), nullable=False)
    merchantUrl = db.Column(db.String(200), nullable=False)

    def __init__(self, accountId, merchantName, merchantUrl):
        self.accountId = accountId
        self.merchantName = merchantName
        self.merchantUrl = merchantUrl
