from flask import Blueprint
from server.auth.controller.account_controller import AccountAPI, GetTokenAPI, TopUpAPI
from server.auth.controller.merchant_controller import SignUpAPI


auth_blueprint = Blueprint('auth', __name__)

# define the API resources
account_view = AccountAPI.as_view('account_api')
merchant_signup_view = SignUpAPI.as_view('signup_api')
token_view = GetTokenAPI.as_view('gettoken_api')
topup_view = TopUpAPI.as_view('topup_api')

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    '/account',
    view_func=account_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/merchant/<accountId>/signup',
    view_func=merchant_signup_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/account/<accountId>/token',
    view_func=token_view,
    methods=['GET']
)
auth_blueprint.add_url_rule(
    '/account/<accountId>/topup',
    view_func=topup_view,
    methods=['POST']
)