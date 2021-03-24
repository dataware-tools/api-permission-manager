#!/usr/bin/env python
# Copyright API authors
"""The API server."""

import os

from dataware_tools_api_helper import get_jwt_payload_from_request
import responder

from api.schemas import ActionSchema
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
        'allow_methods': ['*']
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


@api.route('/actions')
class ActionsResource:
    def on_get(self, _, resp):
        actions_schema = ActionSchema(many=True)
        result = actions_schema.dump(ActionType.list())
        resp.media = {
            'actions': result,
        }


@api.route('/actions/{action_id}')
class ActionResource:
    def on_get(self, _, resp, *, action_id: str):
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
