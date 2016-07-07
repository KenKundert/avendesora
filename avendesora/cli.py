#!/usr/bin/env python3
"""
Avendesora Password Generator

Generates passwords and pass phrases based on stored account information.

usage:
    avendesora [options]
    avendesora [options] <account> [<secret>]

options:
    -a, --all               Output all account information.
    -c, --clipboard         Write output to clipboard rather than stdout.
    -f <text>, --find <text>
                            List any account that contains the given string in 
                            its ID or aliases.
    -g <GPG ID>, --gpgid <GPG ID>
                            Use this GPG ID when creating any missing files.
    -H <plain_text>, --hide <plain_text>
                            Encode plain_text using base64 as a way of hiding 
                            (but not encrypting) its value.
    -I, --init              Create an initial accounts file
    -R <coded_text>, --reveal <coded_text>
                            Decode coded_text using base64.
    -s <text>, --search <text>
                            List any account that contains the given string in 
                            {search_fields} or its ID.
    --stdout                Write output to the standard output without any
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
from .generator import PasswordGenerator
from .gpg import GPG
from .preferences import SETTINGS_DIR, DEFAULT_LOG_FILENAME, SEARCH_FIELDS
from .writer import get_writer
from .utilities import Hidden
from inform import Inform, Error, output, terminate, debug
from shlib import to_path

import docopt
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
    cmdline = docopt.docopt(
        __doc__.format(search_fields=', '.join(SEARCH_FIELDS))
    )
    if cmdline['--hide']:
        debug(cmdline['--hide'])
        output(Hidden.hide(cmdline['--hide']))
        terminate()
    if cmdline['--reveal']:
        output(Hidden.reveal(cmdline['--reveal']))
        terminate()

    def teardown():
        inform.disconnect()
        gpg.close()

    gpg = GPG(gpg_id=cmdline['--gpgid'])
    inform = Inform(
        logfile=gpg.open(to_path(SETTINGS_DIR, DEFAULT_LOG_FILENAME)),
        termination_callback=teardown
    )
    try:
        generator = PasswordGenerator(
            gpg_id = cmdline['--gpgid'],
            init = cmdline['--init']
        )

        # search for accounts that match search criteria
        if cmdline['--find']:
            print_search_results(cmdline['--find'], generator.find_accounts)
            terminate()

        if cmdline['--search']:
            print_search_results(cmdline['--search'], generator.search_accounts)
            terminate()

        # determine the account and output specified information
        account_name = cmdline['<account>']
        writer = get_writer(
            cmdline['<account>'], cmdline['--clipboard'], cmdline['--stdout']
        )
        if account_name:
            account = generator.get_account(account_name)
            if cmdline['--all']:
                account.write_summary()
            if cmdline['<secret>'] or not cmdline['--all']:
                writer.display_field(account, cmdline['<secret>'])
        else:
            account_name, script = generator.discover_account()
            account = generator.get_account(account_name)
            writer.run_script(account, script)

    except KeyboardInterrupt:
        output('Terminated by user.')
    except Error as err:
        err.terminate()

    terminate()
