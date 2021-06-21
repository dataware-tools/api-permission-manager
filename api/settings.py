from enum import Enum
from typing import Dict, List

PAGINATION = {
    'DEFAULT_PER_PAGE': 25,
}

TORTOISE_ORM = {
    'connections': {
        'default': 'sqlite://db.sqlite3'
    },
    'apps': {
        'models': {
            'models': ['api.models', 'aerich.models'],
            'default_connection': 'default',
        }
    },
}


class ActionType(Enum):
    """List of actions."""
    # Database-related actions
    read_databases = 'Read databases'           # Read databases
    add_databases = 'Add databases'             # Add new databases
    update_databases = 'Update databases'       # Update metadata of databases
    delete_databases = 'Delete databases'       # Delete databases

    # Metadata-related actions
    read_metadata = 'Read metadata'               # Read metadata
    add_metadata = 'Write metadata'               # Add new metadata
    update_metadata = 'Update metadata'           # Update metadata of metadata
    delete_metadata = 'Delete metadata'           # Delete metadata

    # Metadata-related actions
    read_private_keys = 'Read private keys in metadata'     # Read private keys

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
