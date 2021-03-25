from enum import Enum
from typing import Dict, List


class ActionType(Enum):
    read_only_public = 'Read only public'
    read_all = 'Read all'
    write = 'Write'

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
            all_actions ()
        """
        all_actions = list(map(lambda c: c.describe(), cls))
        return all_actions
