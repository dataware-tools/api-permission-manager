import json

from api import server
from api.settings import ActionType


class TestRolesResource:
    def test_get_roles_200(self, api, setup_testdb):
        r = api.requests.get(
            url=api.url_for(server.RolesResource),
            params={
                'per_page': 25,
                'page': 1,
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
        # Check content of permissions
        assert isinstance(data['roles'][0]['permissions'][0]['databases'], list)
        assert isinstance(data['roles'][0]['permissions'][0]['actions'], list)
        assert 'action_id' in data['roles'][0]['permissions'][0]['actions'][0].keys()
        assert 'name' in data['roles'][0]['permissions'][0]['actions'][0].keys()

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

    def test_get_roles_200_pagination_contents(self, api, setup_testdb):
        # Get role1 for the first page
        r = api.requests.get(
            url=api.url_for(server.RolesResource),
            params={
                'per_page': 2,
                'page': 1,
            },
        )
        assert r.status_code == 200
        data = json.loads(r.text)
        assert len(data['roles']) == 2
        assert data['roles'][0]['name'] == 'role1'
        assert data['roles'][1]['name'] == 'role2'

        # Get role2 for the second page
        r = api.requests.get(
            url=api.url_for(server.RolesResource),
            params={
                'per_page': 2,
                'page': 2,
            },
        )
        assert r.status_code == 200
        data = json.loads(r.text)
        assert len(data['roles']) == 2
        assert data['roles'][0]['name'] == 'role3'
        assert data['roles'][1]['name'] == 'role4'

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
        assert data['length'] == 4
        assert len(data['roles']) == 4

    def test_get_roles_200_with_per_page_0(self, api, setup_testdb):
        r = api.requests.get(
            url=api.url_for(server.RolesResource),
            params={
                'per_page': 0,
            },
        )
        assert r.status_code == 200
        data = json.loads(r.text)
        assert data['length'] == 4
        assert len(data['roles']) == 4

    def test_get_roles_400_illegal_page_string(self, api):
        r = api.requests.get(
            url=api.url_for(server.RolesResource),
            params={
                'per_page': 25,
                'page': 'expect 400',
                'search': '',
            },
        )
        assert r.status_code == 400

    def test_get_roles_400_illegal_page_0(self, api):
        r = api.requests.get(
            url=api.url_for(server.RolesResource),
            params={
                'per_page': 25,
                'page': 0,
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
                        'action_ids': [ActionType.read_records.name, ActionType.add_records.name],
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

        # Check content of permissions
        assert isinstance(data['permissions'][0]['databases'], list)
        assert isinstance(data['permissions'][0]['actions'], list)
        assert 'action_id' in data['permissions'][0]['actions'][0].keys()
        assert 'name' in data['permissions'][0]['actions'][0].keys()

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

    def test_post_roles_400_action_does_not_exist(self, api):
        r = api.requests.post(
            url=api.url_for(server.RolesResource),
            json={
                'name': 'test role',
                'description': 'test role',
                'permissions': [{
                    'databases': ['database1', 'database2'],
                    'action_ids': ['action_id_that_does_not_exist'],
                }],
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

        # Check content of permissions
        assert isinstance(data['permissions'][0]['databases'], list)
        assert isinstance(data['permissions'][0]['actions'], list)
        assert 'action_id' in data['permissions'][0]['actions'][0].keys()
        assert 'name' in data['permissions'][0]['actions'][0].keys()

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
                'permissions': [
                    {
                        'databases': ['database1', 'database2'],
                        'action_ids': [ActionType.read_records.name],
                    },
                ],
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
        assert len(data['permissions']) == 1

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
        assert len(data['permissions']) == 1

        # --> Check content of permissions
        assert isinstance(data['permissions'][0]['databases'], list)
        assert isinstance(data['permissions'][0]['actions'], list)
        assert 'action_id' in data['permissions'][0]['actions'][0].keys()
        assert 'name' in data['permissions'][0]['actions'][0].keys()

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

    def test_patch_role_400_action_does_not_exist(self, api):
        r = api.requests.patch(
            url=api.url_for(
                server.RoleResource,
                role_id=1,
            ),
            json={
                'permissions': [{
                    'action_ids': ['action_id_that_does_not_exist'],
                }],
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
