import pytest
import os
import rtm.remember_the_milk as rtm
import datetime

"""
tests will require an authenticated auth_token in the configuration file
assuming there is at least one task in the Inbox list
"""


def _rtm_with_api_keys():
    return rtm.RememberTheMilk.load_from_ini(os.environ['RTM_CONFIGURATION'])


def test_obtain_lists():
    r = _rtm_with_api_keys()
    lists = r.obtain_all_lists()
    assert len(lists) > 0
    assert len(lists[0]['id']) > 0
    assert lists[0]['name'] == 'Inbox'
    global inbox_id
    inbox_id = lists[0]['id']


def test_obtain_tasks():
    global inbox_id
    r = _rtm_with_api_keys()
    tasks = r.obtain_tasks_from_list(inbox_id)
    assert len(tasks) > 0
    assert len(tasks[0]['id']) > 0
    assert type(tasks[0]['created']) == datetime.datetime
