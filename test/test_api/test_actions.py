import json

from api import server


class TestActionsResource:
    def test_get_actions_200(self, api):
        r = api.requests.get(url=api.url_for(server.ActionsResource))
        data = json.loads(r.text)
        assert r.status_code == 200
        assert 'actions' in data.keys()


class TestActionResource:
    def test_get_action_200(self, api):
        r = api.requests.get(url=api.url_for(server.ActionResource, action_id='metadata:write'))
        assert r.status_code == 200
        data = json.loads(r.text)
        assert 'action_id' in data.keys()
        assert 'name' in data.keys()

    def test_get_action_404(self, api):
        r = api.requests.get(url=api.url_for(server.ActionResource, action_id='action_that_does_not_exist'))
        assert r.status_code == 404
