# Usage {{{1
"""
Avendesora Collaborative Password Generator

Generates passwords and pass phrases based on stored account information.

Usage:
    avendesora [options] <command> [<args>...]

Options:
    -h, --help        output basic usage information.

Commands:
{commands}

Use 'avendesora help <command>' for information on a specific command.
Use 'avendesora help' for list of available help topics.

Documentation can be found at avendesora.readthedocs.io.
"""

# License {{{1
# Copyright (C) 2016-18 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.


# Imports {{{1
from .command import Command
from .config import read_config, get_setting
from .error import PasswordError
from .gpg import BufferedFile
from .utilities import OSErrors
from .__init__ import __version__, __released__
from . import shlib
from inform import Inform, Error, done, fatal, output, terminate, os_error
from docopt import docopt


# Main {{{1
def main():
    try:
        # read config file
        read_config()

        # read command line
        cmdline = docopt(
            __doc__.format(commands=Command.summarize()),
            version = 'avendesora {} ({})'.format(__version__, __released__),
            options_first = True,
        )

        # start logging
        logfile = BufferedFile(get_setting('log_file'), True)
        Inform(
            logfile=logfile, hanging_indent=False,
            stream_policy='header', notify_if_no_tty=True
        )
        shlib.set_prefs(use_inform=True, log_cmd=True)

        # run the requested command
        Command.execute(cmdline['<command>'], cmdline['<args>'])
        done()
    except KeyboardInterrupt:
        output('\nTerminated by user.')
        terminate()
    except (PasswordError, Error) as e:
        e.terminate()
    except OSErrors as e:
        fatal(os_error(e))
    done()
