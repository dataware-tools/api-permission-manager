#!/usr/bin/env python
# Copyright API authors
"""The API server."""

import os

from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
from dataware_tools_api_helper import get_jwt_payload_from_request
import responder

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


@api.route('/users')
class Users():
    def on_get(self, req: responder.Request, resp: responder.Response):
        """Get users.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response

        """
        # TODO: receive some query string (e.g. per_page)
        auth0 = _get_auth0_client()
        users = auth0.users.list()

        resp.media = users


@api.route('/users/{user_id}')
class User():
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


@api.route('/permissions')
class Permissions():
    def on_get(self, req: responder.Request, resp: responder.Response):
        """Get permissions.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response

        """
        # TODO: implementation
        pass


@api.route('/permissions/{permission_id}')
class Permission():
    def on_get(self, req: responder.Request, resp: responder.Response, *, permission_id: str):
        """Get permission information.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response
            *
            permission_id (str): Permission id

        """
        # TODO: implementation
        pass


@api.route('/healthz')
def healthz(_, resp):
    resp.text = 'ok'


if __name__ == '__main__':
    debug = os.environ.get('API_DEBUG', '') in ['true', 'True', 'TRUE', '1']
    print('Debug: {}'.format(debug))
    api.run(debug=debug)
