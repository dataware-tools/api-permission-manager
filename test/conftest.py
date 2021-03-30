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


@pytest.fixture()
async def setup_testdb():
    # FIXME: Hardcoded user_id that exists on auth0
    existing_user_id = 'auth0|60388ce7fb37d00068262ec4'

    from api.models import RoleModel
    role1 = await RoleModel.create(
        name='role1',
    )
    role2 = await RoleModel.create(
        name='role2',
    )

    from api.models import UserModel
    user = await UserModel.create(
        id=existing_user_id,
        name='test name',
    )
    await user.roles.add(role1, role2)
    return {
        'existing_user_id': existing_user_id,
    }
