import pytest
from tortoise.contrib.test import finalizer, initializer

from api import server


@pytest.fixture
def api():
    return server.api


@pytest.fixture(scope='session', autouse=True)
def initialize_tests(request):
    '''Initialize tests.
    Reference: https://tortoise-orm.readthedocs.io/en/latest/contrib/unittest.html?highlight=test#py-test
    '''
    initializer(['api.models'], app_label='models')
    request.addfinalizer(finalizer)
