#!/usr/bin/env python3
# Usage {{{1
"""
Avendesora Password Generator

Generates passwords and pass phrases based on stored account information.

Usage:
    avendesora [--stdout | --clipboard] value [<account> [<field>]]
    avendesora info <account>
    avendesora [--browser <browser>] browse <account> [<key>]
    avendesora find <text>
    avendesora search <text>
    avendesora [--encoding <encoding>] hide [<text>]
    avendesora [--encoding <encoding>] show [<text>]
    avendesora [--gpgid <id>] init
    avendesora help [<topic>]
    avendesora [--stdout | --clipboard] [<account> [<field>]]

Options:
    -b <browser>, --browser <browser>
                            Open account in browser.
    -c, --clipboard         Write output to clipboard rather than stdout.
    -g <gpg-id>, --gpgid <gpg-id>
                            Use this ID when creating any missing encrypted files.
    -h, --help              Output basic usage information.
    -e <encoding>, --encoding <encoding>
                            Encoding used when concealing information.
    -s, --stdout            Write output to the standard output without any
                            annotation or protections.
"""

# License {{{1
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
from .conceal import Conceal
from .config import read_config, get_setting
from .generator import PasswordGenerator
from .gpg import GnuPG, BufferedFile
from .help import Help
from .writer import get_writer
from inform import Inform, Error, fatal, output, terminate, debug
from shlib import to_path
from docopt import docopt
import sys

# Utilities {{{1
def print_search_results(search_term, search_func):
    to_print = []
    for acct in search_func(search_term):
        aliases = getattr(acct, 'aliases', [])

        aliases = ' (%s)' % (', '.join(aliases)) if aliases else ''
        to_print += [acct.get_name() + aliases]
    output(search_term + ':')
    output('    ' + ('\n    '.join(sorted(to_print))))

# Main {{{1
def main():
    # read config file
    read_config()

    # read command line
    cmdline = docopt(__doc__)

    # initilize GPG
    gpg = GnuPG.initialize(gpg_id=cmdline['--gpgid'])

    # start logging
    logfile=BufferedFile(get_setting('log_file'))
    try:
        with Inform(logfile=logfile, hanging_indent=False):

            # read the command line
            if cmdline['help']:
                Help.show(cmdline['<topic>'])
                terminate()

            # process commands that do not need password generator
            if cmdline['hide']:
                output(Conceal.hide(cmdline['<text>'], cmdline['--encoding']))
                terminate()

            if cmdline['show']:
                output(Conceal.show(cmdline['<text>'], cmdline['--encoding']))
                terminate()

            # run the generator
            generator = PasswordGenerator(gpg, cmdline['init'])

            # search for accounts that match search criteria
            if cmdline['find']:
                print_search_results(
                    cmdline['<text>'], generator.find_accounts
                )
                terminate()

            if cmdline['search']:
                print_search_results(
                    cmdline['<text>'], generator.search_accounts
                )
                terminate()

            # determine the account and output specified information
            account_name = cmdline['<account>']
            writer = get_writer(
                cmdline['<account>'], cmdline['--clipboard'], cmdline['--stdout']
            )
            if account_name:
                account = generator.get_account(account_name)
                if cmdline['browse']:
                    account.open_browser(cmdline['--browser'])
                else:
                    if cmdline['info']:
                        account.write_summary()
                    if cmdline['<field>'] or not cmdline['info']:
                        writer.display_field(account, cmdline['<field>'])
            else:
                # complain if account is required
                if cmdline['browse']:
                    fatal('account missing (required when starting browser).')

                # use discovery to determine account
                account_name, script = generator.discover_account()
                account = generator.get_account(account_name)
                writer.run_script(account, script)

    except KeyboardInterrupt:
        output('Terminated by user.')
    except Error as err:
        err.terminate()
    except OSError as err:
        fatal(os_error(err))

    terminate()
