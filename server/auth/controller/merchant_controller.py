from pdb import post_mortem
from flask import request, make_response, jsonify
from flask.views import MethodView

from server.database import db
from server.models.account_model import Account
from server.models.merchant_model import Merchant

class SignUpAPI(MethodView):
    """
    Sign up an account as merchant
    """
    def post(self, accountId):
        # get the post data
        post_data = request.get_json()
        # check if account is merchant
        account = Account.query.filter_by(accountId=accountId).first()
        if not account.accountType=="merchant":
            responseObject = {
                'status': 'fail',
                'message': 'You are not using merchant account. Please try again.'
            }
            return make_response(jsonify(responseObject)), 202
        else:
            try:
                merchant = Merchant(
                    # accountId=request.url.split('/')[4],
                    accountId=accountId,
                    merchantName=post_data.get('merchantName'),
                    merchantUrl=post_data.get('merchantUrl')
                )
                # insert the merchant account
                db.session.add(merchant)
                db.session.commit()
                responseObject = {
                    'status': 'success',
                    'data': {
                            'merchantName': merchant.merchantName,
                            'accountId': merchant.accountId,
                            'merchantId': merchant.merchantId,
                            'apiKey': merchant.apiKey,
                            'merchantUrl': merchant.merchantUrl
                        }
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject)), 401

