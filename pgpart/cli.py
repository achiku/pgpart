# -*- coding: utf-8 -*-
import click

from . import __version__


class PgpartCLI(click.MultiCommand):

    """Jangle CLI main class"""

    def list_commands(self, ctx):
        """return available modules"""
        return ['rangep', 'listp']

    def get_command(self, ctx, name):
        """get command"""
        try:
            mod = __import__('pgpart.' + name, None, None, ['cli'])
            return mod.cli
        except ImportError:
            pass


cli = PgpartCLI(help="Generate PostgreSQL partitioning DDL (v{0})".format(__version__))


if __name__ == '__main__':
    cli()
