import pytest
import os
import rtm.remember_the_milk as rtm

"""
certain tests work only with a configuration file in place that has a valid api_key and shared_secret
other tests will require an authenticated auth_token in the configuration file
"""


def _rtm_with_api_keys():
    return rtm.RememberTheMilk.load_from_ini(os.environ['RTM_CONFIGURATION'])


def _frob_valid(frob):
    assert type(frob) == str
    assert len(frob) > 8


def test_get_frob():
    r = _rtm_with_api_keys()
    f = r._obtain_frob()
    _frob_valid(f)


def test_desktop_authenticate_pre():
    r = _rtm_with_api_keys()
    frob, user_call_url = r._authenticate_desktop_pre_user_permission(perms='read')
    _frob_valid(frob)
    assert user_call_url.startswith('https://')
    assert 'services/auth' in user_call_url


def test_token_valid():
    """
    requires ini file in place with authenticated auth_token
    """
    r = _rtm_with_api_keys()
    assert r.check_token_valid()
