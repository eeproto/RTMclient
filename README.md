# Remember The Milk API Client

## Purpose

Remember The Milk is an online task management application. They offer an API which at the time of writing is free for
non commercial use. Read more about the API at https://www.rememberthemilk.com/services/api/.

This is a Python client for the RTM API. Developed for personal, non-commercial use.

## Quickstart

Get an [API key](https://www.gnu.org/licenses/gpl-3.0-standalone.html) from RTM and put it into a file `rtm.ini`:

```ini
[settings]
api_key = my_api_key
shared_secret = my_shared_secret
```

Then authenticate and work with the API resources:

```bash
python rtm authenticate rtm.ini

python rtm lists rtm.ini

python rtm tasks rtm.ini 49111194
```

## Usage

Get your API key from https://www.rememberthemilk.com/services/api/keys.rtm. You will receive one string
called `api_key` and one called `shared_secret`.

The module stores these two strings along with information generated through the authentication process in an ini-style
configuration file. Generate a sample/stub ini file with the command

```bash
python rtm configsample
```

You will receive a file `sample.ini` that looks like:

```ini
[settings]
api_key = my_api_key
shared_secret = my_shared_secret
```

Replace `my_api_key` and `my_shared_secret` with your keys and save the file as any file name you like, maybe `rtm.ini`.

RTM uses a multi-step process to authenticate API access for a specific application:

1. Your application generates a unique identifier, called a *frob*.
2. It also generates a URL. Log into your RTM account on your browser and call this URL. Grant access to the API.
3. Your application retrieves an access token from the API.
4. The application uses the token to interact with the API.
5. If at any point the token becomes invalid, we repeat the process.

To run this process, issue this command with the name of your configuration file, and follow the prompts:

```bash
python rtm authenticate rtm.ini
```

Repeat this command to get a new token if at any point your API access does not work anymore.

If you want to revoke API access, log in to your RTM account, go to Settings, Account Settings, Apps, and click "Revoke
access".

Now you are ready to work with the API resources.

To get a list of lists in your account, type

```bash
python rtm lists rtm.ini
```

Each list comes with an ID and a name, separated by a TAB character.

To get a list of tasks in a specific list, type

```bash
python rtm tasks rtm.ini 49111194
```

with the list id you want to access. Tab-separated output includes a task id, task description, and creation timestamp

See `__main__.py` and code in the `tests` folder for examples on how to use this module in your own Python code.

## Tests

[PyTest](https://docs.pytest.org/) tests are in the `tests` folder. To run tests, first create a configuration ini file
and run the authentication process. Pass the configuration file name through the environment
variable `RTM_CONFIGURATION` and make sure to include the source path:

```bash
PYTHONPATH=$(pwd) RTM_CONFIGURATION=rtm.ini pytest tests/
```

## Credit

This module was inspired by work from Sridhar Ratnakumar for https://pypi.org/project/pyrtm/ and
Michael Gruenewald for https://pypi.org/project/RtmAPI/.

## License

[GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0-standalone.html)