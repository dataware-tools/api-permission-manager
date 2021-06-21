import os

import pytest
from tortoise.contrib import test

from api.models import (
    UserModel,
    RoleModel,
)
from api.settings import ActionType


@pytest.fixture()
async def setup_db_for_test_permission_check():
    user_id: str = 'test_user_id'
    from api.models import RoleModel
    role1 = await RoleModel.create(
        name='role1',
        permissions=[{
            'databases': ['database1'],
            'action_ids': [
                ActionType.read_metadata.name,
                ActionType.add_metadata.name,
                ActionType.update_metadata.name,
                ActionType.delete_metadata.name,
                ActionType.read_private_keys.name,
            ],
        }]
    )
    role2 = await RoleModel.create(
        name='role2',
        permissions=[{
            'databases': ['testpostfix*', '*testprefix', 'test?single'],
            'action_ids': [
                ActionType.read_metadata.name,
                ActionType.add_metadata.name,
                ActionType.update_metadata.name,
                ActionType.delete_metadata.name,
            ],
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


class TestUserModel(test.TestCase):

    async def test_adding_user(self):
        user_id = 'test_user_id'
        await UserModel.create(
            id=user_id,
            name='test name',
        )
        user = await UserModel.get(id=user_id)
        assert user.id == user_id

    async def test_adding_user_with_roles(self):
        role1 = await RoleModel.create(
            name='role1',
        )
        role2 = await RoleModel.create(
            name='role2',
        )

        user = await UserModel.create(
            id='test_user_id',
            name='test name',
        )
        await user.roles.add(role1, role2)
        roles = await user.roles.all()
        assert len(roles) == 2


@pytest.mark.asyncio
async def test_is_user_permitted_action(setup_db_for_test_permission_check):
    user = await UserModel.get(id=setup_db_for_test_permission_check['user_id'])
    assert await user.is_user_permitted_action(
        ActionType.read_metadata,
        'testpostfix123123',
    ) is True

    assert await user.is_user_permitted_action(
        ActionType.read_metadata,
        '123123testprefix',
    ) is True

    assert await user.is_user_permitted_action(
        ActionType.read_metadata,
        'test1single',
    ) is True

    assert await user.is_user_permitted_action(
        ActionType.read_metadata,
        'testsingle',
    ) is False

    assert await user.is_user_permitted_action(
        ActionType.read_metadata,
        'should_be_false_database',
    ) is False

    assert await user.is_user_permitted_action(
        ActionType.read_private_keys,
        'testpostfix123123',
    ) is False

    assert await user.is_user_permitted_action(
        ActionType.read_private_keys,
        'database1',
    ) is True

    assert await user.is_user_permitted_action(
        ActionType.add_metadata,
        'database1',
    ) is True


class TestRoleModel(test.TestCase):

    async def test_adding_role(self):
        role = await RoleModel.create(name='role')
        assert role.name == 'role'
