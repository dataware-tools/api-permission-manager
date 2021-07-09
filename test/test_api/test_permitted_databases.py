import json

from api import server


def test_get_permitted_databases(setup_testdb, api):
    r = api.requests.get(
        url=api.url_for(
            server.PermittedDatabasesResource,
        ),
        json={
            'database_ids': ['database1', 'database2', 'database3'],
            'user_id': setup_testdb['existing_user_id'],
        },
    )
    assert r.status_code == 200
    data = json.loads(r.text)
    assert 'database_ids' in data.keys()
    assert 'selected_indices' in data.keys()
    assert data['database_ids'] == ['database3']
    assert data['selected_indices'] == [2]


def test_get_permitted_databases_no_database_id_400(setup_testdb, api):
    r = api.requests.get(
        url=api.url_for(
            server.PermittedDatabasesResource,
        ),
        json={
            'user_id': setup_testdb['existing_user_id'],
        },
    )
    assert r.status_code == 400


def test_get_permitted_databases_invalid_token_403(api):
    r = api.requests.get(
        url=api.url_for(
            server.PermittedDatabasesResource,
        ),
        json={
            'database_ids': ['database1', 'database2', 'database3'],
        },
        headers={'authorization': 'Bearer invalid_token'},
    )
    assert r.status_code == 403
