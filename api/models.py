from typing import Dict, List

from tortoise.models import Model
from tortoise import fields

from api.settings import ActionType
from api.utils import match_exist_in_databases


class UserModel(Model):
    id = fields.CharField(max_length=255, pk=True)
    roles: fields.ManyToManyRelation['RoleModel'] = fields.ManyToManyField(
        'models.RoleModel',
        related_name='roles',
        through='user_role',
    )

    def __str__(self):
        return self.name

    async def get_permitted_actions(self, database_id: str) -> List[ActionType]:
        """Returns permitted actions for the user on the database.

        Args:
            database_id (str)

        Returns:
            (List[ActionType])

        """
        # Get roles for user
        await self.fetch_related('roles')
        roles = self.roles

        # Return empty list if no roles
        if not roles:
            return []

        # TODO: Make it faster by memo
        permitted_actions: Dict[ActionType] = {}
        for role in roles:
            for permission in role.permissions:
                database_patterns = permission['databases']
                # Check if there's match in database patterns
                database_match: bool = match_exist_in_databases(database_id, database_patterns)
                if not database_match:
                    continue
                # Add action to permitted_actions
                for action in permission['action_ids']:
                    permitted_actions[ActionType[action]] = True

        return permitted_actions.keys()

    async def is_user_permitted_action(self, action: ActionType, database_id: str) -> bool:
        """Returns if the user has permission for the action on the database.

        Args:
            user_id (str)
            action (ActionType)
            database_id (str)

        Returns:
            (bool)

        """
        # Get roles for user
        await self.fetch_related('roles')
        roles = self.roles

        # Return false if no roles
        if not roles:
            return False

        # TODO: Make it faster by memo
        for role in roles:
            for permission in role.permissions:
                database_patterns = permission['databases']
                # Check if there's match in database patterns
                database_match: bool = match_exist_in_databases(database_id, database_patterns)
                if not database_match:
                    continue
                # Check if action_ids contains specified action
                if action.name in permission['action_ids']:
                    return True

        return False


class RoleModel(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(default='')
    permissions = fields.JSONField(
        default=[{
            'databases': [],
            'action_ids': [],
        }]
    )

    users: fields.ManyToManyRelation
