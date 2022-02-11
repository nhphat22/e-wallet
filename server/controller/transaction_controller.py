from flask.views import MethodView
from flask import request, make_response, jsonify
from hashlib import md5
import hmac
import json

from server.database import db
from server.models.transaction_model import Transaction
from server.models.merchant_model import Merchant


class CreateTransactionAPI(MethodView):
    def post(self):
        data = request.form.to_dict()
        merchant = Merchant.query.filter_by(merchantId=data["merchantId"]).first()
        hash_key=str(merchant.apiKey)
        signature = hmac.new(hash_key.encode('utf-8'), json.dumps({
                'merchantId': data["merchantId"],
                'amount': float(data["amount"]),
                'extraData': data["extraData"]
            }, sort_keys=True).encode('utf-8'), md5).hexdigest()
        if data["signature"] != signature:
            responseObject = {
                    'status': 'fail',
                    'message': 'Security alert!'
                }
            return make_response(jsonify(responseObject)), 400
        transaction = Transaction(
            merchantId=data["merchantId"],
            amount=data["amount"],
            incomeAccount=merchant.accountId,
            outcomeAccount=None,
            signature=data["signature"]
        )
        # insert the transaction
        # db.session.add(transaction)
        # db.session.commit()
        responseObject = {
            'status': 'success',
            'data': {
                    'merchantId': transaction.merchantId,
                    'incomeAccount': transaction.incomeAccount,
                    'amount': transaction.amount,
                    'signature': transaction.signature
                }
        }
        return make_response(jsonify(responseObject)), 201    
