from flask import Blueprint
from server.controller.account_controller import AccountAPI, GetTokenAPI, TopUpAPI
from server.controller.merchant_controller import SignUpAPI
from server.controller.transaction_controller import CreateTransactionAPI, ConfirmTransactionAPI, VerifyTransactionAPI, CancelTransactionAPI, TransactionStatusAPI


auth_blueprint = Blueprint('auth', __name__)

# define the API resources
account_view = AccountAPI.as_view('account_api')
merchant_signup_view = SignUpAPI.as_view('signup_api')
token_view = GetTokenAPI.as_view('gettoken_api')
topup_view = TopUpAPI.as_view('topup_api')
create_trans_view = CreateTransactionAPI.as_view('create_trans_api')
confirm_trans_view = ConfirmTransactionAPI.as_view('confirm_trans_api')
verify_trans_view = VerifyTransactionAPI.as_view('verify_trans_api')
cancel_trans_view = CancelTransactionAPI.as_view('cancel_trans_api')
test_view = TransactionStatusAPI.as_view('test_api')

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
auth_blueprint.add_url_rule(
    '/transaction/create',
    view_func=create_trans_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/transaction/confirm',
    view_func=confirm_trans_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/transaction/verify',
    view_func=verify_trans_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/transaction/cancel',
    view_func=cancel_trans_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/test',
    view_func=test_view,
    methods=['POST']
)