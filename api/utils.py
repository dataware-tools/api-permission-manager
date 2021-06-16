import fnmatch
import os
from typing import List

from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0


def get_auth0_client():
    # env variables should be defined docker-compose.yaml or .env or ...
    domain = os.environ.get("AUTH0_DOMAIN")
    non_interactive_client_id = os.environ.get("AUTH0_CLIENT_ID")
    non_interactive_client_secret = os.environ.get("AUTH0_CLIENT_SECRET")

    get_token = GetToken(domain)
    token = get_token.client_credentials(non_interactive_client_id,
                                         non_interactive_client_secret, 'https://{}/api/v2/'.format(domain))
    mgmt_api_token = token['access_token']

    auth0 = Auth0(domain, mgmt_api_token)

    return auth0


def build_search_query(search: str):
    """Build search query adapted to length of string.

    Args:
        search (str): Original search string.

    Returns:
        built_query (str): Built query string.

    """
    if len(search) >= 3:
        built_query: str = f'*{search}*'
    else:
        built_query: str = f'{search}*'
    return built_query


def match_exist_in_databases(database_id_to_check: str, database_patterns: List[str]):
    """Check if the matched database_id exists in list of database pattern.

    Args:
        database_id_to_check (str)
        database_patterns (List[str])

    Returns:
        (bool)

    """
    for database_pattern in database_patterns:
        if fnmatch.fnmatch(database_id_to_check, database_pattern):
            return True
    return False
