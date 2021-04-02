import json

from api import server
from api.settings import ActionType


class TestRolesResource:
    def test_get_roles_200(self, api, setup_testdb):
        r = api.requests.get(
            url=api.url_for(server.RolesResource),
            params={
                'per_page': 25,
                'page': 0,
                'search': '',
            },
        )
        assert r.status_code == 200
        data = json.loads(r.text)
        assert 'page' in data.keys()
        assert 'per_page' in data.keys()
        assert 'length' in data.keys()
        assert 'total' in data.keys()
        assert 'roles' in data.keys()
        assert isinstance(data['roles'], list)

        assert isinstance(data['roles'][0]['permissions'], list)

    def test_get_roles_200_out_of_pages(self, api, setup_testdb):
        r = api.requests.get(
            url=api.url_for(server.RolesResource),
            params={
                'per_page': 25,
                'page': 100,
                'search': '',
            },
        )
        assert r.status_code == 200
        data = json.loads(r.text)
        assert data['length'] == 0
        assert len(data['roles']) == 0

    def test_get_roles_200_with_search_does_not_exist(self, api, setup_testdb):
        r = api.requests.get(
            url=api.url_for(server.RolesResource),
            params={
                'search': 'keyword that does not exist',
            },
        )
        assert r.status_code == 200
        data = json.loads(r.text)
        assert data['length'] == 0
        assert len(data['roles']) == 0

    def test_get_roles_200_with_search_does_exist(self, api, setup_testdb):
        r = api.requests.get(
            url=api.url_for(server.RolesResource),
            params={
                'search': 'role',
            },
        )
        assert r.status_code == 200
        data = json.loads(r.text)
        assert data['length'] == 2
        assert len(data['roles']) == 2

    def test_get_roles_200_with_per_page_0(self, api, setup_testdb):
        r = api.requests.get(
            url=api.url_for(server.RolesResource),
            params={
                'per_page': 0,
            },
        )
        assert r.status_code == 200
        data = json.loads(r.text)
        assert data['length'] == 2
        assert len(data['roles']) == 2

    def test_get_roles_400(self, api):
        r = api.requests.get(
            url=api.url_for(server.RolesResource),
            params={
                'per_page': 25,
                'page': 'expect 400',
                'search': '',
            },
        )
        assert r.status_code == 400

    def test_post_roles_201(self, api):
        r = api.requests.post(
            url=api.url_for(server.RolesResource),
            json={
                'name': 'test role',
                'description': 'test role',
                'permissions': [
                    {
                        'databases': ['database1', 'database2'],
                        'actions': [ActionType.read_all.describe(), ActionType.write.describe()],
                    },
                ],
            },
        )
        assert r.status_code == 200

        data = json.loads(r.text)
        assert 'role_id' in data.keys()
        assert data['name'] == 'test role'
        assert data['description'] == 'test role'
        assert len(data['permissions']) > 0

    def test_post_roles_400_invalid_permissions(self, api):
        r = api.requests.post(
            url=api.url_for(server.RolesResource),
            json={
                'name': 'test role',
                'description': 'test role',
                'permissions': [1, 2],
            },
        )
        assert r.status_code == 400

    def test_post_roles_400_name_empty(self, api):
        r = api.requests.post(
            url=api.url_for(server.RolesResource),
            json={
                'description': 'test role',
                'permissions': [],
            },
        )
        assert r.status_code == 400

    def test_post_roles_400_permissions_empty(self, api):
        r = api.requests.post(
            url=api.url_for(server.RolesResource),
            json={
                'name': 'test role',
                'description': 'test role',
            },
        )
        assert r.status_code == 400


class TestRoleResource:
    def test_get_role_200(self, api, setup_testdb):
        r = api.requests.get(
            url=api.url_for(
                server.RoleResource,
                role_id=1,
            ),
        )
        assert r.status_code == 200
        data = json.loads(r.text)
        assert 'role_id' in data.keys()
        assert 'name' in data.keys()
        assert 'description' in data.keys()
        assert 'permissions' in data.keys()
        assert len(data['permissions']) == 1

    def test_get_role_404(self, api, setup_testdb):
        r = api.requests.get(
            url=api.url_for(
                server.RoleResource,
                role_id=10000000,
            ),
        )
        assert r.status_code == 404

    def test_patch_role_200(self, api, setup_testdb):
        r = api.requests.patch(
            url=api.url_for(
                server.RoleResource,
                role_id=1,
            ),
            json={
                'name': 'new name',
                'description': 'new description',
                'permissions': [],
            },
        )
        assert r.status_code == 200
        data = json.loads(r.text)
        assert 'role_id' in data.keys()
        assert 'name' in data.keys()
        assert 'description' in data.keys()
        assert 'permissions' in data.keys()
        assert data['name'] == 'new name'
        assert data['description'] == 'new description'
        assert len(data['permissions']) == 0

        # Re-get object and check content
        r = api.requests.get(
            url=api.url_for(
                server.RoleResource,
                role_id=1,
            ),
        )
        assert r.status_code == 200
        data = json.loads(r.text)
        assert data['name'] == 'new name'
        assert data['description'] == 'new description'
        assert len(data['permissions']) == 0

    def test_patch_role_400(self, api, setup_testdb):
        r = api.requests.patch(
            url=api.url_for(
                server.RoleResource,
                role_id=1,
            ),
            json={
                'name': 'new name',
                'description': 'new description',
                'permissions': 'invalid permissions',
            },
        )
        assert r.status_code == 400

    def test_patch_role_404(self, api, setup_testdb):
        r = api.requests.patch(
            url=api.url_for(
                server.RoleResource,
                role_id=10000000,
            ),
            json={
                'name': 'new name',
                'description': 'new description',
                'permissions': [],
            },
        )
        assert r.status_code == 404

    def test_delete_role_200(self, api, setup_testdb):
        r = api.requests.delete(
            url=api.url_for(
                server.RoleResource,
                role_id=1,
            ),
        )
        assert r.status_code == 200

        # Check if role object deleted
        r = api.requests.get(
            url=api.url_for(
                server.RoleResource,
                role_id=1,
            ),
        )
        assert r.status_code == 404

    def test_delete_role_404(self, api, setup_testdb):
        r = api.requests.delete(
            url=api.url_for(
                server.RoleResource,
                role_id=10000000,
            ),
        )
        assert r.status_code == 404
