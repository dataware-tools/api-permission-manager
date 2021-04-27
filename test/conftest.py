import pytest
from tortoise.contrib.test import finalizer, initializer

from api import server
from api import settings
from api.settings import ActionType
from api.utils import get_auth0_client


@pytest.fixture
def api():
    return server.api


@pytest.fixture(autouse=True)
def initialize_tests(request):
    """Initialize tests.
    Reference: https://tortoise-orm.readthedocs.io/en/latest/contrib/unittest.html?highlight=test#py-test
    """
    initializer(
        settings.TORTOISE_ORM['apps']['models']['models'],
        app_label='models',
    )
    request.addfinalizer(finalizer)


@pytest.fixture(scope='session')
def auth0_existing_userid():
    """Get existing userid from auth0.
    """
    auth0 = get_auth0_client()
    auth0_response = auth0.users.list()
    users = auth0_response['users']
    if len(users) == 0:
        raise ValueError('Please register at least 1 user to auth0.')
    existing_userid = users[0]['user_id']
    return existing_userid


@pytest.fixture()
async def setup_testdb(auth0_existing_userid):
    from api.models import RoleModel
    role1 = await RoleModel.create(
        name='role1',
        permissions=[{
            'databases': ['database1', 'database2'],
            'action_ids': [ActionType.read_all.name, ActionType.write.name],
        }]
    )
    role2 = await RoleModel.create(
        name='role2',
        permissions=[{
            'databases': ['database1', 'database2'],
            'action_ids': [ActionType.read_only_public.name, ActionType.write.name],
        }]
    )
    role3 = await RoleModel.create(
        name='role3',
        permissions=[{
            'databases': ['database1', 'database2'],
            'action_ids': [ActionType.read_only_public.name],
        }]
    )
    role4 = await RoleModel.create(
        name='role4',
    )

    from api.models import UserModel
    user = await UserModel.create(
        id=auth0_existing_userid,
    )
    await user.roles.add(role1, role2, role3, role4)
    return {
        'existing_user_id': auth0_existing_userid,
    }
