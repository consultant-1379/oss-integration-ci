"""The main module for the CI Script Executor."""

import os
import click

plugin_folder = os.path.join(os.path.dirname(__file__), 'bin')


class MyCLI(click.MultiCommand):
    """Used to get a list of the files within bin, then get the commands from each when chosen."""

    def list_commands(self, ctx):
        """List python scripts in the specified directory."""
        file_list = []
        for filename in os.listdir(plugin_folder):
            if filename.endswith('.py') and filename != '__init__.py':
                file_list.append(filename[:-3])
        file_list.sort()
        return file_list

    # pylint: disable=arguments-renamed eval-used
    def get_command(self, ctx, name):
        """Get all the commands from the chosen command."""
        command = {}
        file_name = os.path.join(plugin_folder, name + '.py')
        with open(file_name, "r", encoding="utf-8") as file:
            code = compile(file.read(), file_name, 'exec')
            eval(code, command, command)
        return command['cli']


cli = MyCLI(help='This tool\'s subcommands are loaded from a '
            'plugin folder dynamically.')

if __name__ == '__main__':
    cli()
