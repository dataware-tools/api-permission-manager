import pytest
from tortoise.contrib.test import finalizer, initializer

from api import server
from api.utils import get_auth0_client


@pytest.fixture
def api():
    return server.api


@pytest.fixture(autouse=True)
def initialize_tests(request):
    """Initialize tests.
    Reference: https://tortoise-orm.readthedocs.io/en/latest/contrib/unittest.html?highlight=test#py-test
    """
    initializer(['api.models'], app_label='models')
    request.addfinalizer(finalizer)


@pytest.fixture(scope='session')
def auth0_existing_userid():
    """Get existing userid from auth0.
    """
    auth0 = get_auth0_client()
    auth0_response = auth0.users.list()
    users = auth0_response['users']
    existing_userid = users[0]['user_id']
    return existing_userid


@pytest.fixture()
async def setup_testdb(auth0_existing_userid):
    from api.models import RoleModel
    role1 = await RoleModel.create(
        name='role1',
    )
    role2 = await RoleModel.create(
        name='role2',
    )

    from api.models import UserModel
    user = await UserModel.create(
        id=auth0_existing_userid,
        name='test name',
    )
    await user.roles.add(role1, role2)
    return {
        'existing_user_id': auth0_existing_userid,
    }
