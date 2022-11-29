import remember_the_milk
import click


@click.group()
@click.version_option(version='0.1 ')
def cli():
    pass


@cli.command()
@click.argument('config_file')
def authenticate(config_file):
    """
    Interactive authentication with RTM. Writes authentication information into config file.
    Requires config file with valid api key and shared secret.
    Run command 'configsample' to write a configuration sample file.
    """
    r = remember_the_milk.RememberTheMilk.load_from_ini(config_file)
    r.authenticate_interactive_read_if_necessary()


@cli.command()
@click.argument('config_file')
def lists(config_file):
    """
    Show all lists.
    Requires a config file and successful authentication.
    """
    r = remember_the_milk.RememberTheMilk.load_from_ini(config_file)
    for ll in r.obtain_all_lists():
        print(f"{ll['id']}\t{ll['name']}")


@cli.command()
@click.argument('config_file')
@click.argument('list_id')
def tasks(config_file, list_id):
    """
    Show all open tasks from a list.
    Requires a config file and successful authentication and a valid list id.
    """
    r = remember_the_milk.RememberTheMilk.load_from_ini(config_file)
    for ll in r.obtain_tasks_from_list(list_id, open_tasks_only=True):
        print(f"{ll['id']}\t{ll['name']}\t{str(ll['created'])}")


@cli.command()
def configsample():
    """
    Writes a configuration sapmle to sample.ini
    """
    r = remember_the_milk.RememberTheMilk(
        api_key='my_api_key',
        shared_secret='my_shared_secret'
    )
    r._config_file_name = 'sample.ini'
    r.update_ini_file()


if __name__ == '__main__':
    cli()
