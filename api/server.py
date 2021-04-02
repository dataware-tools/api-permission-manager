#!/usr/bin/env python
# Copyright API authors
"""The API server."""

import os
import urllib.parse

from auth0.v3.exceptions import Auth0Error
from dataware_tools_api_helper import get_jwt_payload_from_request
import responder
from marshmallow import ValidationError
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist
from tortoise.query_utils import Q

from api import settings
from api.models import (
    UserModel,
    RoleModel,
)
from api.schemas import (
    ActionSchema,
    RolesResourceOnGetInputSchema,
    RoleContentSchema,
    RoleSchema,
    UserSchema,
    UsersResourceInputSchema,
    UserResourceOnPatchInputSchema,
)
from api.settings import ActionType
from api.utils import (
    get_auth0_client,
    build_search_query,
)

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

        auth0 = get_auth0_client()
        auth0_response = auth0.users.list(
            page=req_param['page'],
            per_page=req_param['per_page'],
            q=build_search_query(req_param['search']),
        )
        users = auth0_response['users']

        # Add roles for each user if user exists in table
        for user in users:
            try:
                user_data = await UserModel.get(id=user['user_id'])
            except DoesNotExist:
                user_data = None

            if user_data:
                await user_data.fetch_related('roles')
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
        # Unquote user_id
        user_id = urllib.parse.unquote(user_id)

        # Get user info from auth0
        auth0 = get_auth0_client()
        try:
            user = auth0.users.get(id=user_id)
        except Auth0Error as e:
            resp.status_code = 404
            resp.media = {'reason': str(e)}
            return

        # Add roles if user exists in permission database
        try:
            user_data = await UserModel.get(id=user_id)
        except DoesNotExist:
            user_data = None
        if user_data:
            await user_data.fetch_related('roles')
            user['roles'] = user_data.roles
        else:
            user['roles'] = []

        # Serialize user object
        user_schema = UserSchema()
        serialized_user = user_schema.dump(user)

        resp.media = serialized_user

    async def on_patch(self, req: responder.Request, resp: responder.Response, *, user_id: str):
        """Update user role.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response
            *
            user_id (str): User id

        """
        # Unquote user_id
        user_id = urllib.parse.unquote(user_id)

        # Validate request parameters
        try:
            json = await req.media()
            req_param = UserResourceOnPatchInputSchema().load(json)
        except ValidationError as e:
            resp.status_code = 400
            resp.media = {'reason': str(e)}
            return

        # Get user info from auth0
        auth0 = get_auth0_client()
        try:
            user = auth0.users.get(id=user_id)
        except Auth0Error as e:
            resp.status_code = 404
            resp.media = {'reason': str(e)}
            return

        # Get or create user
        user_data, _ = await UserModel.get_or_create(id=user_id)

        # Add roles to permission database
        if 'role_ids' in req_param.keys():
            role_ids = req_param['role_ids']

            # Check if all role_ids exists
            role_ids_not_exist = [role_id for role_id in role_ids if not await RoleModel.exists(id=role_id)]
            if role_ids_not_exist:
                # Return error
                resp.status_code = 404  # TODO: Check if status code suitable
                resp.media = {'reason': f'Role ids {role_ids_not_exist} does not exist.'}
                return

            # Update database
            roles = [await RoleModel.get(id=role_id) for role_id in role_ids]
            await user_data.roles.add(*roles)

            # Update response
            await user_data.fetch_related('roles')
            user['roles'] = user_data.roles

        # Serialize user object
        user_schema = UserSchema()
        serialized_user = user_schema.dump(user)

        resp.media = serialized_user


@api.route('/roles')
class RolesResource():
    async def on_get(self, req: responder.Request, resp: responder.Response):
        """Get roles.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response

        """
        # Validate request parameters
        try:
            req_param = RolesResourceOnGetInputSchema().load(req.params)
        except ValidationError as e:
            resp.status_code = 400
            resp.media = {'reason': str(e)}
            return

        # Get roles
        roles = RoleModel.all()
        if req_param['per_page'] > 0:
            roles = roles.offset(req_param['page']).limit(req_param['per_page'])
        if req_param['search']:
            roles = roles.filter(
                Q(name__contains=req_param['search']) | Q(description__contains=req_param['search'])
            )
        roles = await roles.all()
        number_of_total_roles = await RoleModel.all().count()

        # Serialize role objects
        roles_schema = RoleSchema(many=True)
        serialized_roles = roles_schema.dump(roles)

        resp.media = {
            'page': req_param['page'],
            'per_page': req_param['per_page'],
            'length': len(roles),
            'total': number_of_total_roles,
            'roles': serialized_roles,
        }

    async def on_post(self, req: responder.Request, resp: responder.Response):
        """Create role.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response

        """
        # Validate request parameters
        try:
            json = await req.media()
            req_param = RoleContentSchema().load(json)
        except ValidationError as e:
            resp.status_code = 400
            resp.media = {'reason': str(e)}
            return

        # Create role object
        role = await RoleModel.create(**req_param)

        # Serialize role objects
        role_schema = RoleSchema()
        serialized_role = role_schema.dump(role)

        resp.media = serialized_role


@api.route('/roles/{role_id}')
class RoleResource():
    async def on_get(self, req: responder.Request, resp: responder.Response, *, role_id: str):
        """Get role information.

        Args:
            req (responder.Request): Request
            resp (responder.Response): Response
            *
            role_id (str): Role id

        """
        # Get role object
        role = await RoleModel.get_or_none(id=int(role_id))
        if role is None:
            resp.status_code = 404
            resp.media = {'reason': f'Role roleid={role_id} does not exist.'}
            return

        # Serialize role objects
        role_schema = RoleSchema()
        serialized_role = role_schema.dump(role)

        resp.media = serialized_role

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
