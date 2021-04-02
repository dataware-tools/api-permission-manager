import json

from api import server


def test_healthz(api):
    r = api.requests.get(url=api.url_for(server.healthz))
    assert r.text == 'ok'


def test_index(api):
    r = api.requests.get(url=api.url_for(server.index))
    data = json.loads(r.text)
    assert 'jwt_payload' in data.keys()
