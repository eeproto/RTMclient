import pytest
import rtm.remember_the_milk as rtm


def test_signature():
    r = rtm.RememberTheMilk(api_key='key', shared_secret='BANANAS')
    s = r._api_signature(parameters={
        'yxz': 'foo', 'feg': 'bar', 'abc': 'baz'
    })
    assert s == '82044aae4dd676094f23f1ec152159ba'


def test_auth_url():
    r = rtm.RememberTheMilk(api_key='abc123', shared_secret='BANANAS')
    u = r._build_auth_url(perms='delete', frob='123456')
    assert u == 'https://api.rememberthemilk.com/services/auth/?'\
                'perms=delete&frob=123456&api_key=abc123&api_sig=d36a9750609e3114764af35d9f8a5844'

def test_service_url():
    r = rtm.RememberTheMilk(api_key='abc123', shared_secret='BANANAS')
    u = r._build_service_url(method='rtm.auth.getFrob', method_parameters={})
    assert u == 'https://api.rememberthemilk.com/services/rest/?'\
                'method=rtm.auth.getFrob&format=json&api_key=abc123&api_sig=5c220749da97b71ee02e45e2ed990c04'
