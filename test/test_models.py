import os

import pytest
from tortoise.contrib import test

from api.models import (
    UserModel,
    RoleModel,
    PermissionModel,
)


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


class TestRoleModel(test.TestCase):

    async def test_adding_role(self):
        role = await RoleModel.create(name='role')
        assert role.name == 'role'


class TestPermissionModel(test.TestCase):

    async def test_adding_permission(self):
        role = await RoleModel.create(name='role')
        permission = await PermissionModel.create(
            role=role,
            databases=[
                'database1',
                'database2',
                'database3',
            ],
            actions=[
                'action1',
                'action2',
                'action3',
            ],
        )
        assert 'database1' in permission.databases
        assert 'action1' in permission.actions
