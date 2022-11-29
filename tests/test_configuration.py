import pytest
import tempfile
import rtm.remember_the_milk as rtm

def _my_ini_file():
    return '''
[settings]
api_key = 67keykey
shared_secret = 99secret
'''

def test_load_ini():
    with tempfile.NamedTemporaryFile(mode='w') as ini_file:
        ini_file.write(_my_ini_file())
        ini_file.flush()
        r = rtm.RememberTheMilk.load_from_ini(ini_file.name)
        assert r._api_key == '67keykey'
        assert r._shared_secret == '99secret'

def test_write_ini():
    with tempfile.NamedTemporaryFile(mode='w') as ini_file:
        ini_file.write(_my_ini_file())
        ini_file.flush()
        r = rtm.RememberTheMilk.load_from_ini(ini_file.name)
        r._auth_token = 'token577'
        r._frob = '998877'
        r.update_ini_file()
        with open(ini_file.name, 'r') as readback:
            config = readback.read()
            assert 'token = token577' in config
            assert 'frob = 998877' in config
