import click
from bifrostx.server import start_server
from bifrostx.__version__ import metadata


@click.group
@click.version_option(
    version=metadata["project"]["version"], prog_name=metadata["project"]["name"]
)
def cli():
    pass


@cli.command
def server():
    start_server()


@cli.command
def install():
    # TODO: install extnsions from github or zip
    click.echo("Install Not implemented Yet")


@cli.command
def uninstall():
    # TODO: uninstall extnsions
    click.echo("Uninstall Not implemented Yet")


if __name__ == "__main__":
    cli()
