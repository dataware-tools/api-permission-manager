import pytest

from api.utils import match_exist_in_databases


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
