import binascii
import os

import click

from flask.cli import with_appcontext


@click.command()
@click.argument('bytes', default=32)
@with_appcontext
def secret(bytes):
    """
    Generate a random secret token.

    :return: str
    """
    return click.echo(binascii.b2a_hex(os.urandom(bytes)))
