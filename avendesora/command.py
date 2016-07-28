# Commands

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
from .preferences import INDENT
from .writer import get_writer
from .__init__ import __version__
from inform import Error, error, codicil, output, debug
from shlib import to_path
from docopt import docopt
from textwrap import dedent
import sys


# Utilities {{{1
def title(text):
    return text[0].upper() + text[1:] + '.'

# Command base class {{{1
class Command:
    @classmethod
    def commands(cls):
        for cmd in cls.__subclasses__():
            yield cmd
            for sub in cmd.commands():
                yield sub

    @classmethod
    def commands_sorted(cls):
        for cmd in sorted(cls.commands(), key=lambda c: c.get_name()):
            yield cmd

    @classmethod
    def find(cls, name):
        for command in cls.commands():
            if name in command.NAMES:
                return command

    @classmethod
    def execute(cls, name, args):
        command = cls.find(name)
        if command:
            command.run(name, args if args else [])
        else:
            error('unknown command.', culprit=name)
            codicil("Use 'avendesora help' for list of available commands."),

    @classmethod
    def get_name(cls):
        return cls.NAMES[0]


# Add {{{1
class Add(Command):
    NAMES = 'new', 'add',
    DESC = 'add a new account'
    USAGE = dedent("""
        Usage:
            avendesora [options] new [<prototype>]
            avendesora [options] add [<prototype>]

        Options:
            -f <file>, --file <file>
                                    Add account to specified file.
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(title=title(cls.DESC), usage=cls.USAGE)


# Browse {{{1
class Browse(Command):
    NAMES = 'browse',
    DESC = 'open account URL in web browser'
    USAGE = dedent("""
        Usage:
            avendesora [options] browse <account> [<key>]

        Options:
            -b <browser>, --browser <browser>
                                    Open account in specified browser.
    """).strip()

    @classmethod
    def help(cls):
        default_browser = get_setting('default_browser')
        browsers = get_setting('browsers')
        browsers = '\n'.join([
            '%s%s  %s' % (INDENT, k, browsers[k].split()[0])
            for k in sorted(browsers)
        ])
        text = dedent("""
            {title}

            {usage}

            The default browser is {default}. The available browsers are:
            {browsers}
        """).strip()
        return text.format(
            title=title(cls.DESC), usage=cls.USAGE,
            default=default_browser, browsers=browsers
        )

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # run the generator
        generator = PasswordGenerator()

        # determine the account and open the URL
        account = generator.get_account(cmdline['<account>'])
        account.open_browser(cmdline['--browser'])

# Edit {{{1
class Edit(Command):
    NAMES = 'edit',
    DESC = 'edit an account'
    USAGE = dedent("""
        Usage:
            avendesora edit <account>
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(title=title(cls.DESC), usage=cls.USAGE)


# Find {{{1
class Find(Command):
    NAMES = 'find',
    DESC = 'find an account'
    USAGE = dedent("""
        Find accounts whose name contains the search text.

        Usage:
            avendesora find <text>
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(title=title(cls.DESC), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # run the generator
        generator = PasswordGenerator()

        # find accounts whose name matches the criteria
        to_print = []
        for acct in generator.find_accounts(cmdline['<text>']):
            aliases = getattr(acct, 'aliases', [])

            aliases = ' (%s)' % (', '.join(aliases)) if aliases else ''
            to_print += [acct.get_name() + aliases]
        output(cmdline['<text>']+ ':')
        output('    ' + ('\n    '.join(sorted(to_print))))


# Help {{{1
class Help(Command):
    NAMES = 'help',
    DESC = 'give information about commands or other topics'
    USAGE = dedent("""
        Usage:
            avendesora help [<topic>]
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(title=title(cls.DESC), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        from .help import HelpMessage
        HelpMessage.show(cmdline['<topic>'])


# Hide {{{1
class Hide(Command):
    NAMES = 'hide', 'conceal',
    DESC = 'conceal text by encoding it'
    USAGE = dedent("""
        Usage:
            avendesora [options] hide <text>
            avendesora [options] conceal <text>

        Options:
            -e <encoding>, --encoding <encoding>
                                    Encoding used when concealing information.
    """).strip()

    @classmethod
    def help(cls):
        encodings = '    ' + '\n    '.join(Conceal.encodings())
        text = dedent("""
            {title}

            {usage}

            Possible encodings include:
            {encodings}

            base64 (default):
                This encoding obscures but does not encrypt the text. It can
                protect text from observers that get a quick glance of the
                encoded text, but if they are able to capture it they can easily
                decode it.
        """).strip()
        return text.format(
            title=title(cls.DESC), usage=cls.USAGE, encodings=encodings
        )

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # transform and output the string
        output(Conceal.hide(cmdline['<text>'], cmdline['--encoding']))


# Initialize {{{1
class Initialize(Command):
    NAMES = 'init', 'initialize',
    DESC = 'create initial set of Avendesora files'
    USAGE = dedent("""
        Usage:
            avendesora [options] init
            avendesora [options] initialize

        Options:
            -g <gpg-id>, --gpg-id <gpg-id>
                                    Use this ID when creating any missing encrypted files.
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}

            Initial configuration and accounts files are created only if they
            do not already exist. If you do not give a GPG ID, Avendesora will 
            try to guess it based on your user name and domain name.
        """).strip()
        return text.format(title=title(cls.DESC), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # run the generator
        generator = PasswordGenerator(init=True, gpg_id=cmdline['--gpg-id'])


# Search {{{1
class Search(Command):
    NAMES = 'search',
    DESC = 'search accounts'
    USAGE = dedent("""
        Search for accounts whose values contain the search text.

        Usage:
            avendesora search <text>
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(title=title(cls.DESC), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # run the generator
        generator = PasswordGenerator()

        # search for accounts that match search criteria
        to_print = []
        for acct in generator.search_accounts(cmdline['<text>']):
            aliases = getattr(acct, 'aliases', [])

            aliases = ' (%s)' % (', '.join(aliases)) if aliases else ''
            to_print += [acct.get_name() + aliases]
        output(cmdline['<text>']+ ':')
        output('    ' + ('\n    '.join(sorted(to_print))))


# Show {{{1
class Show(Command):
    NAMES = 'show', 's',
    DESC = 'show an account value'
    USAGE = dedent("""
        Produce an account value. If the value is secret, it is produced only
        temporarily unless --stdout is specified.

        Usage:
            avendesora show [--stdout | --clipboard] [<account> [<field>]]
            avendesora s [--stdout | --clipboard] [<account> [<field>]]

        Options:
            -c, --clipboard         Write output to clipboard rather than stdout.
            -s, --stdout            Write output to the standard output without
                                    any annotation or protections.
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(title=title(cls.DESC), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # run the generator
        generator = PasswordGenerator()

        # determine the account and output specified information
        account_name = cmdline['<account>']
        writer = get_writer(
            bool(account_name), cmdline['--clipboard'], cmdline['--stdout']
        )
        if account_name:
            account = generator.get_account(account_name)
            writer.display_field(account, cmdline['<field>'])
        else:
            # use discovery to determine account
            account_name, script = generator.discover_account()
            account = generator.get_account(account_name)
            writer.run_script(account, script)


# ShowAll {{{1
class ShowAll(Command):
    NAMES = 'all', 'showall',
    DESC = 'display all account values'
    USAGE = dedent("""
        Show all account values.

        Usage:
            avendesora all <account>
            avendesora showall <account>
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(title=title(cls.DESC), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # run the generator
        generator = PasswordGenerator()

        # determine the account
        account = generator.get_account(cmdline['<account>'])
        account.write_summary()

# Unhide {{{1
class Unhide(Command):
    NAMES = 'unhide', 'reveal',
    DESC = 'reveal concealed text'
    USAGE = dedent("""
        Transform concealed text to reveal its original form.

        Usage:
            avendesora [options] unhide <text>
            avendesora [options] reveal <text>

        Options:
            -e <encoding>, --encoding <encoding>
                                    Encoding used when revealing information.
    """).strip()

    @classmethod
    def help(cls):
        encodings = '    ' + '\n    '.join(Conceal.encodings())
        text = dedent("""
            {title}

            {usage}

            Possible encodings include:
            {encodings}

            base64 (default):
                This encoding obscures but does not encrypt the text. It can
                protect text from observers that get a quick glance of the
                encoded text, but if they are able to capture it they can easily
                decode it.
        """).strip()
        return text.format(
            title=title(cls.DESC), usage=cls.USAGE, encodings=encodings
        )

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # transform and output the string
        output(Conceal.show(cmdline['<text>'], cmdline['--encoding']))


# Version {{{1
class Version(Command):
    NAMES = 'version',
    DESC = 'display Avendesora version'
    USAGE = dedent("""
        Usage:
            avendesora version
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(title=title(cls.DESC), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # output the version
        output('Avendesora version: %s' % __version__)

