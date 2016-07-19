#!/usr/bin/env python3
# Usage {{{1
"""
Avendesora Password Generator

Generates passwords and pass phrases based on stored account information.

usage:
    avendesora [options]
    avendesora [options] <account> [<secret>]

options:
    -a, --all               Output all account information.
    -b, --browse            Open account in the default browser ({defbrowser}).
    -B <choice>, --browser <choice>
                            Open account in specified browser.  Choose from
                            {browsers}.
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
                            its ID or in any field value that is not encrypted
                            or concealed.
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
from .config import read_config, get_setting
from .generator import PasswordGenerator
from .gpg import GnuPG
from .preferences import SETTINGS_DIR
from .secrets import Hidden
from .writer import get_writer
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
    # read config file
    read_config()
    browsers = get_setting('browsers')
    browsers = ', '.join(
        ['%s (%s)' % (k, browsers[k].split()[0]) for k in sorted(browsers)]
    )

    # read command line
    cmdline = docopt.docopt(
        __doc__.format(
            defbrowser=get_setting('default_browser'), browsers=browsers
        )
    )

    # start logging
    def teardown():
        inform.disconnect()
        gpg.close()
    gpg = GnuPG(gpg_id=cmdline['--gpgid'])
    inform = Inform(
        logfile=gpg.open(to_path(SETTINGS_DIR, get_setting('log_file'))),
        termination_callback=teardown
    )

    # process hide/reveal commands
    if cmdline['--hide']:
        debug(cmdline['--hide'])
        output(Hidden.hide(cmdline['--hide']))
        terminate()
    if cmdline['--reveal']:
        output(Hidden.reveal(cmdline['--reveal']))
        terminate()

    # run the generator
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
            if cmdline['--browse'] or cmdline['--browser']:
                account.open_browser(cmdline['--browser'])
            else:
                if cmdline['--all']:
                    account.write_summary()
                if cmdline['<secret>'] or not cmdline['--all']:
                    writer.display_field(account, cmdline['<secret>'])
        else:
            # complain if account is required
            if cmdline['--browse'] or cmdline['--browser']:
                fatal('account missing (required when starting browser).')

            # use discovery to determine account
            account_name, script = generator.discover_account()
            account = generator.get_account(account_name)
            writer.run_script(account, script)

    except KeyboardInterrupt:
        output('Terminated by user.')
    except Error as err:
        err.terminate()

    terminate()
