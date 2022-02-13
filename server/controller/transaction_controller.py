from flask.views import MethodView
from flask import request, make_response, jsonify
from hashlib import md5
import hmac
import json

from server.database import db
from server.middleware.jwt_helper import token_required
from server.models.transaction_model import Transaction
from server.models.merchant_model import Merchant
from server.models.account_model import Account


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
            extraData=data["extraData"],
            signature=data["signature"]
        )
        # insert the transaction
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

class ConfirmTransactionAPI(MethodView):
    @token_required
    def post(self, current_acc):
        post_data = request.get_json()
        if not current_acc.accountType=="personal":
            responseObject = {
                'status': 'fail',
                'message': 'You have not connected to an personal account. Please try again.'
            }
            return make_response(jsonify(responseObject)), 202 
        else:
            try:
                transaction = Transaction.query.filter_by(transactionId=post_data["transactionId"]).first()
                account = Account.query.filter_by(accountId=current_acc.accountId).first()
                transaction.confirm_outcomeAccount(account.accountId)
                db.session.commit()
                if transaction.check_confirmation(account.balance):
                    transaction.update_status("CONFIRMED")
                    db.session.commit()
                else:
                    transaction.update_status("FAILED")
                    db.session.commit()
                responseObject = {
                    'status': 'success',
                    'message': 'Transaction has been confirmed.'
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject)), 401

class VerifyTransactionAPI(MethodView):
    @token_required
    def post(self, current_acc):
        post_data = request.get_json()
        if not current_acc.accountType=="personal":
            responseObject = {
                'status': 'fail',
                'message': 'You have not connected to an personal account. Please try again.'
            }
            return make_response(jsonify(responseObject)), 202 
        else:
            try:
                transaction = Transaction.query.filter_by(transactionId=post_data["transactionId"]).first()
                outcomeAccount = Account.query.filter_by(accountId=transaction.outcomeAccount).first()
                incomeAccount = Account.query.filter_by(accountId=transaction.incomeAccount).first()
                if transaction.status == "VERIFIED":
                    responseObject = {
                        'status': 'success',
                        'message': 'Transaction had already been verified.'
                    }
                    return make_response(jsonify(responseObject)), 201
                if transaction.check_confirmation(outcomeAccount.balance):
                    transaction.update_status("VERIFIED")
                    outcomeAccount.update_balance(-transaction.amount)
                    incomeAccount.update_balance(transaction.amount)
                    db.session.commit()
                else:
                    transaction.update_status("FAILED")
                    db.session.commit()
                responseObject = {
                    'status': 'success',
                    'message': 'Transaction has been verified.'
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject)), 401

class CancelTransactionAPI(MethodView):
    @token_required
    def post(self, current_acc):
        post_data = request.get_json()
        if not current_acc.accountType=="personal":
            responseObject = {
                'status': 'fail',
                'message': 'You have not connected to an personal account. Please try again.'
            }
            return make_response(jsonify(responseObject)), 202 
        else:
            try:
                transaction = Transaction.query.filter_by(transactionId=post_data["transactionId"]).first()
                if transaction.status == "CANCELED":
                    responseObject = {
                        'status': 'success',
                        'message': 'Transaction had already been cancelled.'
                    }
                    return make_response(jsonify(responseObject)), 201
                transaction.update_status("CANCELED")
                db.session.commit()
                responseObject = {
                    'status': 'success',
                    'message': 'Transaction has been cancelled.'
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject)), 401
                