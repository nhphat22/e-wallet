from flask import request, make_response, jsonify
from flask.views import MethodView

from server.database import db
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
                accountType=post_data.get('accountType')
            )
            # insert the account
            db.session.add(account)
            db.session.commit()
            # generate the auth token
            auth_token = account.encode_auth_token(account.accountId.hex).encode("utf-8")
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