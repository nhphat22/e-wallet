from flask import request, make_response, jsonify
from flask.views import MethodView

from server.database import db
from server.middleware.jwt_helper import token_required
from server.models.account_model import Account

class AccountAPI(MethodView):
    """
    Create e-wallet account
    """
    def post(self):
        # get the post data
        post_data = request.get_json()
        try:
            account = Account(
                accountType=post_data.get('accountType'),
            )
            # insert the account
            db.session.add(account)
            db.session.commit()
            # generate the auth token
            # auth_token = account.encode_auth_token(account.accountId.hex).encode("utf-8")
            responseObject = {
                'status': 'success',
                'data': {
                        'accountType': account.accountType,
                        'accountId': account.accountId
                    }
                # 'auth_token': auth_token.decode()
            }
            return make_response(jsonify(responseObject)), 201
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Some error occurred. Please try again.'
            }
            return make_response(jsonify(responseObject)), 401

class GetTokenAPI(MethodView):
    """
    Get accountId and accountType token 
    """
    def get(self, accountId):
        # get the post data
        try:
            account = Account.query.filter_by(accountId=accountId).first()
            auth_token = account.encode_auth_token(account.accountId.hex, account.accountType).encode("utf-8")
          
            responseObject = {
                'status': 'success',
                'token': auth_token.decode()
            }
            # print(account.decode_auth_token(auth_token))
            return make_response(jsonify(responseObject)), 201
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'Some error occurred. Please try again.'
            }
            return make_response(jsonify(responseObject)), 401
class TopUpAPI(MethodView):
    """
    Get accountId and accountType token 
    """
    @token_required("issuer")
    def post(self, current_acc, accountId):
        # get the post data
        post_data = request.get_json()
        # check issuer account
        if not current_acc.accountType=="issuer":
            responseObject = {
                'status': 'fail',
                'message': 'You have not connected to an issuer account. Please try again.'
            }
            return make_response(jsonify(responseObject)), 202
        else:
            try:
                account = Account.query.filter_by(accountId=accountId).first()
                account.update_balance(post_data.get('amount'))
                db.session.commit()
                responseObject = {
                    'status': 'success',
                    'data': {
                        'balance': account.balance
                    }
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject)), 401