from enum import Enum, EnumMeta
import os
from typing import Dict, List

PAGINATION = {
    'DEFAULT_PER_PAGE': 25,
}

TORTOISE_ORM = {
    'connections': {
        'default': os.environ.get('DB_URL', 'sqlite://db.sqlite3')
    },
    'apps': {
        'models': {
            'models': ['api.models', 'aerich.models'],
            'default_connection': 'default',
        }
    },
}


class ActionTypeMeta(EnumMeta):
    """Metaclass of ActionType."""

    def __new__(mcs, cls, bases, classdict):
        """Set actions."""

        # Database-related actions
        classdict['databases'] = 'Admin databases'
        classdict['databases:read'] = 'Read databases'
        classdict['databases:write'] = 'Write databases'
        classdict['databases:write:add'] = 'Add databases'
        classdict['databases:write:update'] = 'Update databases'
        classdict['databases:write:delete'] = 'Delete databases'

        # Metadata-related actions
        classdict['metadata'] = 'Admin metadata'
        classdict['metadata:read'] = 'Read metadata'
        classdict['metadata:read:public'] = 'Read public metadata'
        classdict['metadata:write'] = 'Write metadata'
        classdict['metadata:write:add'] = 'Add metadata'
        classdict['metadata:write:update'] = 'Update metadata'
        classdict['metadata:write:delete'] = 'Delete metadata'

        return super().__new__(mcs, cls, bases, classdict)


class ActionType(Enum, metaclass=ActionTypeMeta):
    """List of actions."""

    def describe(self) -> Dict[str, str]:
        """Returns action as a dict object.

        Args:
            None

        Returns:
            action (Dict[str, str])
        """
        action = {
            'action_id': self.name,
            'name': self.value,
        }
        return action

    @classmethod
    def list(cls) -> List[Dict[str, str]]:
        """Returns list of all actions.

        Args:
            None

        Returns:
            all_actions (List[Dict[str, str]]): List of all actions.
        """
        all_actions = list(map(lambda c: c.describe(), cls))
        return all_actions

    @classmethod
    def keys(cls):
        """Returns list of keys of ActionType.

        Args:
            None

        Returns:
            all_keys (List[stri]): List of keys of actions.
        """
        all_keys = list(map(lambda c: c.name, cls))
        return all_keys
