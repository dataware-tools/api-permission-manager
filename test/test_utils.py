import pytest

from api.settings import ActionType
from api.utils import is_user_permitted_action, match_exist_in_databases


def test_match_exist_in_databases():
    assert match_exist_in_databases(
        'database1',
        ['database1', 'database2', 'database3'],
    ) is True

    assert match_exist_in_databases(
        'database4',
        ['database1', 'database2', 'database3'],
    ) is False

    assert match_exist_in_databases(
        'database1',
        ['database*', 'database1', 'database2', 'database3'],
    ) is True

    assert match_exist_in_databases(
        'test_database',
        ['*database', 'database1', 'database2', 'database3'],
    ) is True

    assert match_exist_in_databases(
        'test_database_test',
        ['*database*', 'database1', 'database2', 'database3'],
    ) is True

    assert match_exist_in_databases(
        'database9',
        ['database?', 'database1', 'database2', 'database3'],
    ) is True


@pytest.fixture()
async def setup_db_for_test_permission_check():
    user_id: str = 'test_user_id'
    from api.models import RoleModel
    role1 = await RoleModel.create(
        name='role1',
        permissions=[{
            'databases': ['database1'],
            'action_ids': [ActionType.read_all.name, ActionType.write.name],
        }]
    )
    role2 = await RoleModel.create(
        name='role2',
        permissions=[{
            'databases': ['testpostfix*', '*testprefix', 'test?single'],
            'action_ids': [ActionType.read_only_public.name],
        }]
    )
    from api.models import UserModel
    user = await UserModel.create(
        id=user_id,
    )
    await user.roles.add(role1, role2)
    return {
        'user_id': user_id,
    }


@pytest.mark.asyncio
async def test_is_user_permitted_action(setup_db_for_test_permission_check):
    assert await is_user_permitted_action(
        setup_db_for_test_permission_check['user_id'],
        ActionType.read_only_public,
        'testpostfix123123',
    ) is True

    assert await is_user_permitted_action(
        setup_db_for_test_permission_check['user_id'],
        ActionType.read_only_public,
        '123123testprefix',
    ) is True

    assert await is_user_permitted_action(
        setup_db_for_test_permission_check['user_id'],
        ActionType.read_only_public,
        'test1single',
    ) is True

    assert await is_user_permitted_action(
        setup_db_for_test_permission_check['user_id'],
        ActionType.read_only_public,
        'testsingle',
    ) is False

    assert await is_user_permitted_action(
        setup_db_for_test_permission_check['user_id'],
        ActionType.read_only_public,
        'should_be_false_database',
    ) is False

    assert await is_user_permitted_action(
        setup_db_for_test_permission_check['user_id'],
        ActionType.read_only_public,
        'database1',
    ) is False

    assert await is_user_permitted_action(
        setup_db_for_test_permission_check['user_id'],
        ActionType.read_all,
        'database1',
    ) is True

    assert await is_user_permitted_action(
        setup_db_for_test_permission_check['user_id'],
        ActionType.write,
        'database1',
    ) is True
