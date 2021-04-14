import json
import urllib.parse

from api import server


class TestUsersResource:
    def test_get_users_200(self, api):
        r = api.requests.get(
            url=api.url_for(server.UsersResource),
            params={
                'per_page': 25,
                'page': 0,
                'search': '',
            },
        )
        data = json.loads(r.text)
        assert r.status_code == 200
        assert 'page' in data.keys()
        assert 'per_page' in data.keys()
        assert 'length' in data.keys()
        assert 'total' in data.keys()
        assert 'users' in data.keys()
        assert isinstance(data['users'], list)

    def test_get_users_400(self, api):
        r = api.requests.get(
            url=api.url_for(server.UsersResource),
            params={
                'per_page': 25,
                'page': 'expect 400',
                'search': '',
            },
        )
        assert r.status_code == 400

    def test_prevent_per_page_over_100(self, api):
        r = api.requests.get(
            url=api.url_for(server.UsersResource),
            params={
                'per_page': 101,
                'page': 0,
                'search': '',
            },
        )
        assert r.status_code == 400


class TestUserResource:
    def test_get_user_200(self, api, setup_testdb):
        r = api.requests.get(
            url=api.url_for(
                server.UserResource,
                user_id=urllib.parse.quote(setup_testdb['existing_user_id']),
            ),
        )
        assert r.status_code == 200

        data = json.loads(r.text)
        assert len(data['roles']) > 0
        assert 'role_id' in data['roles'][0].keys()
        assert 'name' in data['roles'][0].keys()

    def test_get_user_404(self, api):
        r = api.requests.get(
            url=api.url_for(
                server.UserResource,
                user_id='user_id_that_does_not_exist',
            ),
        )
        assert r.status_code == 404

    def test_patch_user_200(self, api, setup_testdb):
        r = api.requests.patch(
            url=api.url_for(
                server.UserResource,
                user_id=urllib.parse.quote(setup_testdb['existing_user_id']),
            ),
            json={
                'role_ids': [1, 2],
            },
        )
        assert r.status_code == 200
        data = json.loads(r.text)
        assert 'user_id' in data.keys()
        assert 'name' in data.keys()
        assert 'roles' in data.keys()
        assert len(data['roles']) == 2

    def test_patch_user_200_on_new_user(self, api, auth0_existing_userid):
        '''Test adding roles to new user on DB.'''
        r = api.requests.patch(
            url=api.url_for(
                server.UserResource,
                user_id=urllib.parse.quote(auth0_existing_userid),
            ),
            json={
                'role_ids': [],
            },
        )
        assert r.status_code == 200
        data = json.loads(r.text)
        assert 'user_id' in data.keys()
        assert 'name' in data.keys()
        assert 'roles' in data.keys()
        assert len(data['roles']) == 0

    def test_patch_user_400(self, api, setup_testdb):
        r = api.requests.patch(
            url=api.url_for(
                server.UserResource,
                user_id=urllib.parse.quote(setup_testdb['existing_user_id']),
            ),
            json={
                'role_ids': 1,
            },
        )
        assert r.status_code == 400

    def test_patch_user_404_user(self, api, setup_testdb):
        r = api.requests.patch(
            url=api.url_for(
                server.UserResource,
                user_id='user_id_that_does_not_exist',
            ),
            json={
                'role_ids': [1, 2],
            },
        )
        assert r.status_code == 404

    def test_patch_user_404_role_id(self, api, setup_testdb):
        r = api.requests.patch(
            url=api.url_for(
                server.UserResource,
                user_id=urllib.parse.quote(setup_testdb['existing_user_id']),
            ),
            json={
                'role_ids': [1, 2, 1000],
            },
        )
        assert r.status_code == 404
