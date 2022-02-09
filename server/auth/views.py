from flask import Blueprint
from server.auth.controller.account_controller import AccountAPI


auth_blueprint = Blueprint('auth', __name__)

# define the API resources
account_view = AccountAPI.as_view('account_api')

# add Rules for API Endpoints
auth_blueprint.add_url_rule(
    '/account',
    view_func=account_view,
    methods=['POST']
)