from flask import request, jsonify
from functools import wraps
import jwt

from server.models.account_model import Account

# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(self, *args, **kwargs):
        auth_token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            auth_token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not auth_token:
            return jsonify({'message' : 'Token is missing !!'}), 401

        try:
            # decoding the payload to fetch the stored details
            payload = jwt.decode(
                auth_token, 
                'SECRET_KEY',
                algorithms='HS256'
            )
            current_acc = Account.query.filter_by(accountId = payload['accountId']).first()
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return f(self, current_acc, *args, **kwargs)
  
    return decorated