#!/usr/bin/env python
# Copyright API authors
"""The API server."""

import os

from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
from auth0.v3.exceptions import Auth0Error
from dataware_tools_api_helper import get_jwt_payload_from_request
import responder
from marshmallow import ValidationError
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

from api import settings
from api.models import UserModel
from api.schemas import (
    ActionSchema,
    UserSchema,
    UsersResourceInputSchema,
)
from api.settings import ActionType

# Metadata
description = "An API template."
terms_of_service = "http://tools.hdwlab.com/terms/"
contact = {
    "name": "API Support",
    "url": "http://tools.hdwlab.com/support",
    "email": "contact@hdwlab.co.jp",
}
license = {
    "name": "Apache 2.0",
    "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
}

# Initialize app
api = responder.API(
    title="API Template",
    version="1.0",
    openapi="3.0.2",
    docs_route='/docs',
    description=description,
    terms_of_service=terms_of_service,
    contact=contact,
    license=license,
    cors=True,
    cors_params={
        'allow_origins': ['*'],
        'allow_methods': ['*'],
        'allow_headers': ['*']
    },
    secret_key=os.environ.get('SECRET_KEY', os.urandom(12))
)


@api.on_event('startup')
async def start_db_connection():
    await Tortoise.init(
        db_url=settings.DATABASE_SETTING['HOST'],
        modules={'models': [settings.DATABASE_SETTING['MODELS']]}
    )


@api.on_event('shutdown')
async def close_db_connection():
    await Tortoise.close_connections()


@api.route('/')
def index(req, resp):
    """Index page."""
    jwt_payload = get_jwt_payload_from_request(req)
    res = {
        'jwt_payload': jwt_payload
    }
    resp.media = res


@api.route('/echo/{content}/{resp_type}')
def echo(_, resp, *, content, resp_type):
    if resp_type == 'json':
        resp.media = {'content': content}
    else:
        resp.text = content


def _get_auth0_client():
    # env variables should be defined docker-compose.yaml or .env or ...
    domain = os.environ.get("AUTH0_DOMAIN")
    non_interactive_client_id = os.environ.get("AUTH0_CLIENT_ID")
    non_interactive_client_secret = os.environ.get("AUTH0_CLIENT_SECRET")

    get_token = GetToken(domain)
    token = get_token.client_credentials(non_interactive_client_id,
                                         non_interactive_client_secret, 'https://{}/api/v2/'.format(domain))
    mgmt_api_token = token['access_token']

    auth0 = Auth0(domain, mgmt_api_token)

    return auth0


def _build_search_query(search: str):
    """Build search query adapted to length of string.

    Args:
        search (str): Original search string.

    Returns:
        built_query (str): Built query string.

    """
    if len(search) >= 3:
        built_query: str = f'*{search}*'
    else:
        built_query: str = f'{search}*'
    return built_query


@api.route('/users')
class UsersResource():
    async def on_get(self, req: responder.Request, resp: responder.Response):
        """Get users.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response

        """
        try:
            req_param = UsersResourceInputSchema().load(req.params)
        except ValidationError as e:
            resp.status_code = 400
            resp.media = {'reason': str(e)}
            return

        auth0 = _get_auth0_client()
        auth0_response = auth0.users.list(
            page=req_param['page'],
            per_page=req_param['per_page'],
            q=_build_search_query(req_param['search']),
        )
        users = auth0_response['users']

        # Add roles for each user if user exists in table
        for user in users:
            try:
                user_data = await UserModel.get(id=user['user_id'])
            except DoesNotExist:
                user_data = None

            if user_data:
                user['roles'] = user_data.roles
            else:
                user['roles'] = []

        # Serialize user objects
        users_schema = UserSchema(many=True)
        serialized_users = users_schema.dump(users)

        resp.media = {
            'page': req_param['page'],
            'per_page': req_param['per_page'],
            'length': auth0_response['length'],
            'total': auth0_response['total'],
            'users': serialized_users,
        }


@api.route('/users/{user_id}')
class UserResource():
    async def on_get(self, req: responder.Request, resp: responder.Response, *, user_id: str):
        """Get user role.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response
            *
            user_id (str): User id

        """
        auth0 = _get_auth0_client()
        try:
            user = auth0.users.get(id=user_id)
        except Auth0Error as e:
            resp.status_code = 404
            resp.media = {'reason': str(e)}
            return

        # Add roles if user exists in permission database
        try:
            user_data = await UserModel.get(id=user['user_id'])
        except DoesNotExist:
            user_data = None
        if user_data:
            user['roles'] = user_data.roles
        else:
            user['roles'] = []

        # Serialize user object
        user_schema = UserSchema()
        serialized_user = user_schema.dump(user)

        resp.media = serialized_user

    def on_post(self, req: responder.Request, resp: responder.Response, *, user_id: str):
        """Update user role.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response
            *
            user_id (str): User id

        """
        # TODO: implementation
        pass


@api.route('/roles')
class Roles():
    def on_get(self, req: responder.Request, resp: responder.Response):
        """Get roles.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response

        """
        # TODO: implementation
        pass

    def on_post(self, req: responder.Request, resp: responder.Response):
        """Create role.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response

        """
        # TODO: implementation
        pass


@api.route('/roles/{role_id}')
class Role():
    def on_get(self, req: responder.Request, resp: responder.Response, *, role_id: str):
        """Get role information.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response
            *
            role_id (str): Role id

        """
        # TODO: implementation
        pass

    def on_post(self, req: responder.Request, resp: responder.Response, *, role_id: str):
        """Update role information.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response
            *
            role_id (str): Role id

        """
        # TODO: implementation
        pass

    def on_delete(self, req: responder.Request, resp: responder.Response, *, role_id: str):
        """Delete role.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response
            *
            role_id (str): Role id

        """
        # TODO: implementation
        pass


@api.route('/actions')
class ActionsResource:
    def on_get(self, req: responder.Request, resp: responder.Response):
        """Get permissions.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response

        """
        actions_schema = ActionSchema(many=True)
        result = actions_schema.dump(ActionType.list())
        resp.media = {
            'actions': result,
        }


@api.route('/actions/{action_id}')
class ActionResource:
    def on_get(self, req: responder.Request, resp: responder.Response, *, action_id: str):
        """Get permission information.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response
            *
            action_id (str): Action id

        """
        try:
            action_data = ActionType[action_id].describe()
        except KeyError:
            resp.status_code = 404
            resp.media = {'reason': f'Action {action_id} does not exist.'}
            return

        resp.status_code = 200
        action_schema = ActionSchema()

        result = action_schema.dump(action_data)
        resp.media = result


@api.route('/healthz')
def healthz(_, resp):
    resp.text = 'ok'


if __name__ == '__main__':
    debug = os.environ.get('API_DEBUG', '') in ['true', 'True', 'TRUE', '1']
    print('Debug: {}'.format(debug))
    api.run(debug=debug)
