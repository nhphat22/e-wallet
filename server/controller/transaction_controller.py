from flask.views import MethodView
from flask import request, make_response, jsonify, current_app
from hashlib import md5
import hmac
import json
import requests
import threading

from server.database import db
from server.middleware.jwt_helper import token_required
from server.models.transaction_model import Transaction
from server.models.merchant_model import Merchant
from server.models.account_model import Account


def signature_hashing(key, data):
    hash_key=str(key)
    data_copy = data.copy()
    data_copy.pop("signature")
    for key, value in data_copy.items():
        if data_copy[key].isdecimal():
            data_copy[key] = int(value)
        elif data_copy[key].replace('.', '', 1).isdecimal():
            data_copy[key] = float(value)
    signature = hmac.new(hash_key.encode('utf-8'), 
            json.dumps(data_copy, sort_keys=True).encode('utf-8'), md5).hexdigest()
    return signature

def check_completed_transaction(transactionId):
    from server import app
    with app.app_context():
        transaction = Transaction.query.filter_by(transactionId=transactionId).first()
        if transaction.status != "COMPLETED":
            transaction.update_status("EXPIRED")
            db.session.commit()

class CreateTransactionAPI(MethodView):
    @token_required("merchant")
    def post(self, current_merchant):
        data = request.form.to_dict()
        try:
            if str(current_merchant.merchantId) != data["merchantId"]:
                responseObject = {
                    'status': 'fail',
                    'message': 'Token of merchant and merchant ID are not match.'
                }
                return make_response(jsonify(responseObject)), 401

            merchant = Merchant.query.filter_by(merchantId=data["merchantId"]).first()
            
            if data["signature"] != signature_hashing(merchant.apiKey, data):
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

            threading.Timer(300, check_completed_transaction, [transaction.transactionId]).start()
            
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
        except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject)), 401

class ConfirmTransactionAPI(MethodView):
    @token_required("personal")
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
                if transaction.status == "INITIALIZED":
                    account = Account.query.filter_by(accountId=current_acc.accountId).first()
                    transaction.confirm_outcomeAccount(account.accountId)
                    db.session.commit()
                    if transaction.check_confirmation(account.balance):
                        transaction.update_status("CONFIRMED")
                        db.session.commit()
                        responseObject = {
                            'status': 'success',
                            'message': 'Transaction has been confirmed.'
                        }
                    else:
                        transaction.update_status("FAILED")
                        db.session.commit()
                        responseObject = {
                            'status': 'fail',
                            'message': 'Your balance is not enough for payment.'
                        }
                    data = {
                            "orderId": transaction.extraData,
                            "status": transaction.status
                        }
                    r = requests.post('http://host.docker.internal:5000' + '/update_status_order', data=data)                 
                    return make_response(jsonify(responseObject)), 201
                else: 
                    responseObject = {
                        'status': 'fail',
                        'message': 'Confirmation failed.'
                    }
                    return make_response(jsonify(responseObject)), 401
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject)), 401

class VerifyTransactionAPI(MethodView):
    @token_required("personal")
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
                if transaction.status in ["EXPIRED", "FAILED"]:
                    responseObject = {
                        'status': 'success',
                        'message': 'Transaction is failed.'
                    }
                    return make_response(jsonify(responseObject)), 202
                if transaction.status != "CONFIRMED":
                    responseObject = {
                        'status': 'success',
                        'message': 'You need to confirm your transaction first.'
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
                data = {
                        "orderId": transaction.extraData,
                        "status": transaction.status
                    }
                try:
                    r = requests.post('http://host.docker.internal:5000' + '/update_status_order', data=data)
                    transaction.update_status("COMPLETED")
                    db.session.commit()
                    data['status']=transaction.status
                    r = requests.post('http://host.docker.internal:5000' + '/update_status_order', data=data)
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': 'Some error occurred. Please try again.'
                    }
                    return make_response(jsonify(responseObject)), 401   
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
    @token_required("personal")
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
                data = {
                        "orderId": transaction.extraData,
                        "status": transaction.status
                    }
                r = requests.post('http://host.docker.internal:5000' + '/update_status_order', data=data)
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
                