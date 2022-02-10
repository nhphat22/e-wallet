from server.database import db
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
import jwt

class Account(db.Model):
    __tablename__ = "accounts"

    accountId = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    accountType = db.Column(db.Enum("merchant", "personal", "issuer", name="acc_type", create_type=False), nullable=False)
    balance = db.Column(db.Float, nullable=False)

    def __init__(self, accountType):
        self.accountType = accountType
        self.balance = 0
    
    def topup(self, amount):
        self.balance += amount

    def encode_auth_token(self, accountId, accountType):
        """
        Generates the Auth Token
        """
        try:
            payload = {
                'accountId': accountId,
                'accountType': accountType
            }
            return jwt.encode(
                payload,
                'SECRET_KEY',
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        """
        try:
            payload = jwt.decode(
                auth_token, 
                'SECRET_KEY',
                algorithms='HS256'
            )
            return payload
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'