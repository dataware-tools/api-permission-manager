import json

from api import server
from api.settings import ActionType


def test_is_permitted_200(setup_testdb, api):
    r = api.requests.get(
        url=api.url_for(
            server.PermittedActionResource,
            action_id=ActionType.read_all.name,
        ),
        params={
            'database_id': 'database1',
            'user_id': setup_testdb['existing_user_id'],
        },
    )
    assert r.status_code == 200
    data = json.loads(r.text)
    assert data is True

    r = api.requests.get(
        url=api.url_for(
            server.PermittedActionResource,
            action_id=ActionType.read_all.name,
        ),
        params={
            'database_id': 'database10',
            'user_id': setup_testdb['existing_user_id'],
        },
    )
    assert r.status_code == 200
    data = json.loads(r.text)
    assert data is False


def test_is_permitted_no_database_id_400(setup_testdb, api):
    r = api.requests.get(
        url=api.url_for(
            server.PermittedActionResource,
            action_id=ActionType.read_all.name,
        ),
        params={
            'user_id': setup_testdb['existing_user_id'],
        },
    )
    assert r.status_code == 400


def test_is_permitted_invalid_token_403(api):
    r = api.requests.get(
        url=api.url_for(
            server.PermittedActionResource,
            action_id=ActionType.read_all.name,
        ),
        params={
            'database_id': 'database1',
        },
        headers={'authorization': 'Bearer invalid_token'},
    )
    assert r.status_code == 403
