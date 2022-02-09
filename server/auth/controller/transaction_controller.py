from flask import request, make_response, jsonify
from flask.views import MethodView

from server.database import db
from server.models.transaction_model import Transaction

class Test(MethodView):
    """

    """
    def post(self):
        # get the post data
        post_data = request.get_json()
        # check if product already exists
        transaction = Transaction.query.filter_by(accountId=post_data.get('accountId')).first()
        print(transaction)
        if not transaction:
            try:
                transaction = Transaction(
                    accountId=post_data.get('accountId'),
                    accountAddress=post_data.get('accountAddress')
                )
                print(transaction)
                # insert the user
                db.session.add(transaction)
                db.session.commit()
                responseObject = {
                    'status': 'success',
                    'message': 'Success',
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
        else:
            responseObject = {
                'status': 'fail',
                'message': 'abc.',
            }
        print(transaction)
        return make_response(jsonify(responseObject)), 202