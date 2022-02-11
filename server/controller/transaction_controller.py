from flask.views import MethodView
from flask import request, make_response, jsonify

from server.database import db
from server.models.transaction_model import Transaction

class CreateTransactionAPI(MethodView):
    def post(self):
        print(request.form)
        transaction = Transaction(
            merchantId=request.form["merchantId"],
            amount=request.form["amount"],
            incomeAccount="9c7d101d-dcec-41b6-9627-8e15cd5bc6b8",
            outcomeAccount=None,
            signature=request.form["signature"]
        )
        # insert the merchant account
        db.session.add(transaction)
        db.session.commit()
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
