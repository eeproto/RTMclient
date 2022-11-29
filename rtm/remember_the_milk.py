import os.path
import urllib.parse
import hashlib
from configparser import ConfigParser
from typing import Tuple
from datetime import datetime
import requests


class RtmException(Exception):
    pass


class RtmRequestFailedException(RtmException):
    def __str__(self):
        return f"Request {self.args[0]} failed. Status: {self.args[1]}, reason: {self.args[2]}."


class RememberTheMilk:
    _api_url_base = "https://api.rememberthemilk.com/"
    _auth_path = 'services/auth/'
    _rest_path = "services/rest/"

    def __init__(self, api_key, shared_secret, frob=None, auth_token=None, config_file_name=None):
        self._api_key = api_key
        self._shared_secret = shared_secret
        self._frob = frob
        self._auth_token = auth_token
        self._config_file_name = config_file_name
        self._browser = requests.Session()
        self._browser.headers.update({'Cache-Control': 'no-cache, max-age=0'})
        self._browser.headers.update({'Accept': 'application/json;'})
        self._browser.headers.update({'Content-Type': 'application/json'})

    @classmethod
    def load_from_ini(cls, ini_file):
        config = ConfigParser()
        assert os.path.exists(ini_file), f"Configuration file {ini_file} not found."
        config.read(ini_file)
        r = RememberTheMilk(
            api_key=config.get('settings', 'api_key'),
            shared_secret=config.get('settings', 'shared_secret'),
            frob=config.get('settings', 'frob', fallback=None),
            auth_token=config.get('settings', 'token', fallback=None),
            config_file_name=ini_file
        )
        return r

    def update_ini_file(self):
        if self._config_file_name is None:
            raise Exception('No configuration file name set.')
        with open(self._config_file_name, 'w') as cfile:
            config = ConfigParser()
            config.add_section('settings')
            config['settings']['api_key'] = self._api_key
            config['settings']['shared_secret'] = self._shared_secret
            if self._frob is not None:
                config['settings']['frob'] = self._frob
            if self._auth_token is not None:
                config['settings']['token'] = self._auth_token
            config.write(cfile)

    def _api_signature(self, parameters: dict) -> str:
        """
        generates the api_sig according to https://www.rememberthemilk.com/services/api/authentication.rtm
        yxz=foo feg=bar abc=baz
         becomes abc=baz feg=bar yxz=foo
         becomes abcbazfegbaryxzfoo
         becomes SHAREDSECRETabcbazfegbaryxzfoo
         gets MD5'd
        """
        concat = self._shared_secret + "".join("".join(tup) for tup in sorted(parameters.items()))
        md5 = hashlib.md5()
        md5.update(concat.encode('ascii'))
        return md5.hexdigest()

    def _build_api_url(self, path: str, parameters: dict) -> str:
        """
        generate URL for API calls, see _build_auth_url and _build_service_url for details
        :param parameters: query parameters
        :return: URL string
        """
        url_parts = list(urllib.parse.urlparse(self._api_url_base))
        url_parts[2] = path
        parameters = parameters
        parameters['api_key'] = self._api_key
        parameters['api_sig'] = self._api_signature(parameters)
        url_parts[4] = urllib.parse.urlencode(parameters)
        return urllib.parse.urlunparse(url_parts)

    def _build_auth_url(self, perms: str, frob: str) -> str:
        """
        generates the auth URL according to https://www.rememberthemilk.com/services/api/authentication.rtm
        :param perms: either of read, write, delete
        :param frob: frob as obtained from a previous call
        :return: URL string
        """
        return self._build_api_url(
            path=self._auth_path,
            parameters={
                'perms': perms,
                'frob': frob,
            })

    def _build_service_url(self, method: str, method_parameters: dict, authenticate: bool = False) -> str:
        """
        generates an API service call URL according to https://www.rememberthemilk.com/services/api/request.rest.rtm
        :param method: one of the methods listed in https://www.rememberthemilk.com/services/api/methods.rtm
        :param method_parameters: method parameters
        :param authenticate: add authentication
        :return: URL string
        """
        parameters = method_parameters.copy()
        parameters['method'] = method
        parameters['format'] = 'json'
        if authenticate:
            assert self._auth_token, "authenticate before calling this function"
            parameters['auth_token'] = self._auth_token
        return self._build_api_url(
            path=self._rest_path,
            parameters=parameters
        )

    def _issue_api_request(self, url: str) -> dict:
        """
        Send HTTP request to the API
        :param url: API endpoint URL with query parameters
        :return: dict-style content if the API returns an ok status, or raise RtmRequestFailedException
        """
        response = self._browser.get(url)
        if not response.status_code == requests.codes.ok:
            response.raise_for_status()
        content = response.json()
        status = content['rsp']['stat']
        if status != 'ok':
            raise RtmRequestFailedException(
                'to API', content['rsp']['err']['code'], content['rsp']['err']['msg']
            )
        return content['rsp']

    def _obtain_frob(self) -> str:
        """
        Get a frob from the API, required in authentication process. Does not require authentication.
        :return:
        """
        api_response = self._issue_api_request(
            self._build_service_url(
                method='rtm.auth.getFrob',
                method_parameters={}
            )
        )
        return api_response['frob']

    def _obtain_auth_token(self, frob: str) -> str:
        """
        Get an authentication token for future requests from the API.
        Requires that the user has granted access.
        :param frob: frob used in the authentication request
        :return:
        """
        api_response = self._issue_api_request(
            self._build_service_url(
                method='rtm.auth.getToken',
                method_parameters={
                    'frob': frob
                }
            )
        )
        return api_response['auth']['token']

    def check_token_valid(self) -> bool:
        """
        Checks if the authentication token we have is still valid.
        :return: True if token is valid.
        """
        try:
            api_response = self._issue_api_request(
                self._build_service_url(
                    method='rtm.auth.checkToken',
                    method_parameters={
                        'api_key': self._api_key,
                        'auth_token': self._auth_token
                    }
                )
            )
            return api_response['stat'] == 'ok'
        except RtmRequestFailedException as ex:
            return False

    def _authenticate_desktop_pre_user_permission(self, perms: str) -> (str, str):
        """
        Generates a frob, which we will need later to get an authentication token.
        Generates a URL for the user to call in order to grant us permission. Linked through the frob.
        :param perms: Requested permissions.
        :return: Tuple of the frob and the user URL
        """
        frob = self._obtain_frob()
        permission_url = self._build_auth_url(
            perms=perms,
            frob=frob
        )
        return frob, permission_url

    def _authenticate_desktop_post_user_permission(self, frob: str) -> str:
        """
        Convert the frob into an authentication token. Requires prior authorization from the user.
        :param frob: frob we had used to start user authorization.
        :return: Token to be used for future requests.
        """
        auth_token = self._obtain_auth_token(frob=frob)
        return auth_token

    def authenticate_desktop_interactive(self, permissions: str) -> Tuple[str, str]:
        """
        Interactive process to get from zero to authentication token
        :param permissions: Requested permissions
        :return: frob and token to be stored and used later.
        """
        frob, permission_url = self._authenticate_desktop_pre_user_permission(
            perms=permissions
        )
        print(f'We got frob {frob} from the API. Now open the URL {permission_url} to grant access.')
        input('Hit Enter to continue.')
        auth_token = self._authenticate_desktop_post_user_permission(
            frob=frob)
        print(f'Got auth token {auth_token}.')
        return frob, auth_token

    def authenticate_interactive_read_if_necessary(self):
        """
        Checks if the token we have is valid. If we don't have one, or it is invalid, run the interactive
          authentication process. Store the result in our configuration file.
        :return: Nothing
        """
        if self._auth_token:
            print(f'Have authentication token.')
            if self.check_token_valid():
                print(f'Token is valid. Done here.')
                need_new_token = False
            else:
                print(f'Token is not valid. Applying for a new one.')
                self._auth_token = None
                self._frob = None
                need_new_token = True
        else:
            need_new_token = True
        if need_new_token:
            self._frob, self._auth_token = self.authenticate_desktop_interactive(
                permissions='read'
            )
            print(f'Saving to configuration file {self._config_file_name}.')
            self.update_ini_file()

    def obtain_all_lists(self) -> list:
        """
        Get a list of the user's lists.
        :return: List of dictionaries, one per list, with name and id.
        """
        api_response = self._issue_api_request(
            self._build_service_url(
                method='rtm.lists.getList',
                method_parameters={},
                authenticate=True
            )
        )
        return [{
            'id': ll['id'],
            'name': ll['name']
        } for ll in api_response['lists']['list']
        ]

    def obtain_tasks_from_list(self, list_id: str, open_tasks_only: bool = True) -> list:
        """
        Get a list of tasks in a list.
        :return: List of dictionaries, one per list, with name and id.
        """
        api_response = self._issue_api_request(
            self._build_service_url(
                method='rtm.tasks.getList',
                method_parameters={
                    'list_id': list_id
                },
                authenticate=True
            )
        )
        return [{
            'id': tt['id'],
            'name': tt['name'],
            'created': datetime.strptime(tt['created'], "%Y-%m-%dT%H:%M:%SZ")
        } for tt in api_response['tasks']['list'][0]['taskseries']
            if not (tt['task'][0]['completed'] and open_tasks_only)
        ]
