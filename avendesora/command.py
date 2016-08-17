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
from .config import read_config, get_setting, override_setting
from .editors import GenericEditor
from .generator import PasswordGenerator
from .gpg import GnuPG, PythonFile
from .obscure import Obscure
from .utilities import two_columns, to_python, items, split
from .writer import get_writer
from .__init__ import __version__
from inform import (
    Error, error, codicil, output, conjoin, os_error,
    is_collection, is_str
)
from shlib import to_path, mv
from docopt import docopt
from textwrap import dedent, fill, indent
    # use indent from textwrap rather than inform
    # the inform indent removes spaces from the right side, which causes
    # spurious difference when running changed command
import re
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
    def summarize(cls, width=16):
        summaries = []
        for cmd in Command.commands_sorted():
            summaries.append(two_columns(', '.join(cmd.NAMES), cmd.DESCRIPTION))
        return '\n'.join(summaries)

    @classmethod
    def get_name(cls):
        return cls.NAMES[0]


# Add {{{1
class Add(Command):
    NAMES = 'add', 'a'
    DESCRIPTION = 'add a new account'
    USAGE = dedent("""
        Usage:
            avendesora [options] add [<template>]
            avendesora [options] a   [<template>]

        Options:
            -f <file>, --file <file>
                                    Add account to specified file.
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}

            The default template is {default}. The available templates are:
            {templates}
        """).strip()
        return text.format(
            title=title(cls.DESCRIPTION), usage=cls.USAGE,
            default=get_setting('default_account_template'),
            templates=conjoin(sorted(get_setting('account_templates').keys()))
        )

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        try:
            # get the specified template
            templates = get_setting('account_templates')
            if cmdline['<template>']:
                template_name = cmdline['<template>']
            else:
                template_name = get_setting('default_account_template')
            template = dedent(templates[template_name]).strip() + '\n'

            # save template to tmp file and open it in the editor
            from tempfile import mktemp
            tmpfile = GnuPG(mktemp(suffix='_avendesora.gpg'))
            tmpfile.save(template, get_setting('gpg_ids'))
            GenericEditor.open_and_search(tmpfile.path)

            # read the tmp file and determine if it has changed
            new = tmpfile.read()
            tmpfile.remove()
            if new == template:
                return output('Unchanged, and so ignored.')

            # hide the values that should be hidden
            def hide(match):
                return 'Hidden(%r)' % Obscure.hide(match.group(1))
            new = re.sub("<<(.*?)>>", hide, new)

            # determine the accounts file
            prefix = cmdline['--file']
            if prefix:
                candidates = [
                    p
                    for p in get_setting('accounts_files')
                    if p.startswith(prefix)
                ]
                if not candidates:
                    raise Error('not found.', cuplrit=cmdline['--file'])
                if len(candidates) > 1:
                    raise Error(
                        'ambiguous, matches %s.' % conjoin(candidates),
                        cuplrit=prefix
                    )
                filename = candidates[0]
            else:
                filename = get_setting('accounts_files')[0]
            path = to_path(get_setting('settings_dir'), filename)

            # get original contents of accounts file
            orig_accounts_file = PythonFile(path)
            accounts = orig_accounts_file.run()
            gpg_ids = accounts.get('gpg_ids')

            # add new account to the contents
            accounts = orig_accounts_file.code + new + '\n'

            # rename the original file and then save the new version
            orig_accounts_file.rename('.saved')
            new_accounts_file = GnuPG(path)
            new_accounts_file.save(accounts, gpg_ids)
        except OSError as err:
            error(os_error(err))
        except KeyError as err:
            error(
                'unknown account template, choose from %s.' % conjoin(
                    sorted(templates.keys())
                ), culprit=template_name
            )


# Archive {{{1
class Archive(Command):
    NAMES = 'archive', 'A'
    DESCRIPTION = 'generates archive of all account information'
    USAGE = dedent("""
        Usage:
            avendesora archive
            avendesora A
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(
            title=title(cls.DESCRIPTION), usage=cls.USAGE,
        )

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # run the generator
        generator = PasswordGenerator()

        # get dictionary that fully describes the contents of each account
        entries = []
        for account in generator.all_accounts():
            entry = account.archive()
            if entry:
                entries.append(indent('%r: %s,' % (
                    account.get_name(), to_python(entry)
                ), '    '))

        # build file contents
        from .preferences import ARCHIVE_FILE_CONTENTS
        import arrow
        contents = ARCHIVE_FILE_CONTENTS.format(
            encoding = get_setting('encoding'),
            date=str(arrow.now()),
            accounts = '\n\n'.join(entries)
        )

        archive_file = get_setting('archive_file')
        archive = GnuPG(archive_file)
        if not archive.will_encrypt():
            warn('archive file is not encrypted.', culprit=archive_file)
        try:
            archive.save(contents)
        except OSError as err:
            raise Error(os_error(err), culprit=archive_file)



# Browse {{{1
class Browse(Command):
    NAMES = 'browse', 'b'
    DESCRIPTION = 'open account URL in web browser'
    USAGE = dedent("""
        Usage:
            avendesora [options] browse <account> [<key>]
            avendesora [options] b      <account> [<key>]

        Options:
            -b <browser>, --browser <browser>
                                    Open account in specified browser.
    """).strip()

    @classmethod
    def help(cls):
        default_browser = get_setting('default_browser')
        browsers = get_setting('browsers')
        browsers = '\n'.join([
            two_columns(k, browsers[k].split()[0], width=1)
            for k in sorted(browsers)
        ])
        text = dedent("""
            {title}

            {usage}

            The default browser is {default}. The available browsers are:
            {browsers}
        """).strip()
        return text.format(
            title=title(cls.DESCRIPTION), usage=cls.USAGE,
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
        account.open_browser(cmdline['--browser'], cmdline['<key>'])

# Changed {{{1
class Changed(Command):
    NAMES = 'changed', 'C'
    DESCRIPTION = 'identify any changes that have occurred since the archive was created'
    USAGE = dedent("""
        Usage:
            avendesora changed
            avendesora C
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(
            title=title(cls.DESCRIPTION), usage=cls.USAGE,
        )

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # read archive file
        archive_path = get_setting('archive_file')
        f = PythonFile(archive_path)
        archive = f.run()
        import arrow
        created = archive.get('CREATED')
        if created:
            created = arrow.get(created).format('YYYY-MM-DD hh:mm:ss A ZZ')
            output('archive created: %s' % created)
        archive_accounts = archive.get('ACCOUNTS')
        if not archive_accounts:
            raise Error(
                'corrupt archive, ACCOUNTS missing.', culprit=archive_path
            )

        # run the generator
        generator = PasswordGenerator()

        # determine the account and open the URL
        current_accounts = {}
        for account in generator.all_accounts():
            entry = account.archive()
            if entry:
                current_accounts[account.get_name()] = entry

        # report any new or missing accounts
        new = current_accounts.keys() - archive_accounts.keys()
        missing = archive_accounts.keys() - current_accounts.keys()
        for each in sorted(new):
            output('new account:', each)
        for each in sorted(missing):
            output('missing account:', each)

        # for the common accounts, report any differences in the fields
        common = archive_accounts.keys() & current_accounts.keys()
        for account_name in sorted(common):
            archive_account = archive_accounts[account_name]
            current_account = current_accounts[account_name]

            # report any new or missing fields
            new = current_account.keys() - archive_account.keys()
            missing = archive_account.keys() - current_account.keys()
            for each in sorted(new):
                output(account_name, 'new field', each, sep=': ')
            for each in sorted(missing):
                output(account_name, 'new field', each, sep=': ')

            # for the common fields, report any differences in the values
            shared = archive_account.keys() & current_account.keys()
            for field_name in sorted(shared):
                archive_value = archive_account[field_name]
                current_value = current_account[field_name]
                if is_collection(current_value):
                    archive_items = items(archive_account[field_name])
                    current_items = items(current_account[field_name])
                    archive_keys = set(k for k, v in archive_items)
                    current_keys = set(k for k, v in current_items)
                    new = current_keys - archive_keys
                    missing = archive_keys - current_keys
                    for each in sorted(new):
                        output(account_name, field_name, 'new member', each, sep=': ')
                    for each in sorted(missing):
                        output(account_name, field_name, 'missing member', each, sep=': ')
                    for k in sorted(archive_keys & current_keys):
                        if str(archive_value[k]) != str(current_value[k]):
                            output(account_name, 'member differs', '%s[%s]' % (field_name, k), sep=': ')
                else:
                    if dedent(str(archive_value)) != dedent(str(current_value)):
                        output(account_name, 'field differs', field_name, sep=': ')


# Conceal {{{1
class Conceal(Command):
    NAMES = 'conceal', 'c'
    DESCRIPTION = 'conceal text by encoding it'
    USAGE = dedent("""
        Usage:
            avendesora [options] conceal [<text>]
            avendesora [options] c       [<text>]

        Options:
            -e <encoding>, --encoding <encoding>
                                    Encoding used when concealing information.
    """).strip()

    @classmethod
    def help(cls):
        encodings = '    ' + '\n    '.join(Obscure.encodings())
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

            Though available as an option for convenience, you should not pass
            the text to be hidden as an argument as it is possible for others to
            examine the commands you run and their argument list. For any
            sensitive secret, you should simply run 'avendesora conceal' and
            then enter the secret text when prompted.
        """).strip()
        return text.format(
            title=title(cls.DESCRIPTION), usage=cls.USAGE, encodings=encodings
        )

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # get the text
        text = cmdline['<text>']
        if not text:
            import getpass
            try:
                text = getpass.getpass('text: ')
            except EOFError:
                return

        # transform and output the string
        output(Obscure.hide(text, cmdline['--encoding']))


# Edit {{{1
class Edit(Command):
    NAMES = 'edit', 'e'
    DESCRIPTION = 'edit an account'
    USAGE = dedent("""
        Usage:
            avendesora edit <account>
            avendesora e    <account>
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(title=title(cls.DESCRIPTION), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # run the generator
        generator = PasswordGenerator()

        # determine the account and open the URL
        account = generator.get_account(cmdline['<account>'])
        filepath = account._file_info.path
        account_name = account.__name__
        GenericEditor.open_and_search(filepath, account_name)


# Find {{{1
class Find(Command):
    NAMES = 'find', 'f'
    DESCRIPTION = 'find an account'
    USAGE = dedent("""
        Find accounts whose name contains the search text.

        Usage:
            avendesora find <text>
            avendesora f    <text>
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(title=title(cls.DESCRIPTION), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # run the generator
        generator = PasswordGenerator()

        # find accounts whose name matches the criteria
        to_print = []
        for acct in generator.find_accounts(cmdline['<text>']):
            aliases = split(getattr(acct, 'aliases', []))

            aliases = ' (%s)' % (', '.join(aliases)) if aliases else ''
            to_print += [acct.get_name() + aliases]
        output(cmdline['<text>']+ ':')
        output('    ' + ('\n    '.join(sorted(to_print))))


# Help {{{1
class Help(Command):
    NAMES = 'help', 'h'
    DESCRIPTION = 'give information about commands or other topics'
    USAGE = dedent("""
        Usage:
            avendesora help [<topic>]
            avendesora h    [<topic>]
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(title=title(cls.DESCRIPTION), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        from .help import HelpMessage
        HelpMessage.show(cmdline['<topic>'])


# Initialize {{{1
class Initialize(Command):
    NAMES = 'initialize', 'I'
    DESCRIPTION = 'create initial set of Avendesora files'
    USAGE = dedent("""
        Usage:
            avendesora initialize [--gpg-id <id>]... [options]
            avendesora I          [--gpg-id <id>]... [options]

        Options:
            -g <id>, --gpg-id <id>  Use this ID when creating any missing encrypted files.
            -h <path>, --gpg-home <path>
                                    GPG home directory (default is ~/.gnupg).
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}

            Initial configuration and accounts files are created only if they
            do not already exist.  Existing files are not modified.
        """).strip()
        return text.format(title=title(cls.DESCRIPTION), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)
        if cmdline['--gpg-home']:
            override_setting('gpg_home', cmdline['--gpg-home'])

        # save the gpg_ids for the logfile in case it is encrypted.
        gpg_ids = cmdline['--gpg-id']
        if not get_setting('gpg_ids'):
            override_setting('gpg_ids', gpg_ids)

        # run the generator
        generator = PasswordGenerator(init=True, gpg_ids=gpg_ids)


# New {{{1
class New(Command):
    NAMES = 'new', 'N'
    DESCRIPTION = 'create new accounts file'
    USAGE = dedent("""
        Usage:
            avendesora new [--gpg-id <id>]... <name>
            avendesora N   [--gpg-id <id>]... <name>

        Options:
            -g <id>, --gpg-id <id>  Use this ID when creating any missing encrypted files.
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}

            Creates a new accounts file. Accounts that share the same file share
            the same master password by default and, if the file is encrypted,
            can be decrypted by the same recipients.

            Generally you would create a new accounts file for each person or
            group with which you wish to share accounts. You would use separate
            files for passwords with different security domains. For example, a
            high-value passwords might be placed in an encrypted file that would
            only be placed highly on protected computers. Conversely, low-value
            passwords might be contained in perhaps an unencrypted file that is
            found on many computers.

            Add a '.gpg' extension to <name> to encrypt the file.
        """).strip()
        return text.format(title=title(cls.DESCRIPTION), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # get the gpg ids of those who will be able to decrypt the file
        gpg_ids = cmdline['--gpg-id']
        if not gpg_ids:
            gpg_ids = get_setting('gpg_ids', [])

        # run the generator
        generator = PasswordGenerator(
            init=cmdline['<name>'], gpg_ids=sorted(set(gpg_ids))
                # docopt sometimes duplicates the gpg_ids
        )


# Reveal {{{1
class Reveal(Command):
    NAMES = 'reveal', 'r'
    DESCRIPTION = 'reveal concealed text'
    USAGE = dedent("""
        Transform concealed text to reveal its original form.

        Usage:
            avendesora [options] reveal [<text>]
            avendesora [options] r      [<text>]

        Options:
            -e <encoding>, --encoding <encoding>
                                    Encoding used when revealing information.
    """).strip()

    @classmethod
    def help(cls):
        encodings = '    ' + '\n    '.join(Obscure.encodings())
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

            Though available as an option for convenience, you should not pass
            the text to be revealed as an argument as it is possible for others
            to examine the commands you run and their argument list. For any
            sensitive secret, you should simply run 'avendesora reveal' and then
            enter the encoded text when prompted.
        """).strip()
        return text.format(
            title=title(cls.DESCRIPTION), usage=cls.USAGE, encodings=encodings
        )

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # get the text
        text = cmdline['<text>']
        if not text:
            import getpass
            try:
                text = getpass.getpass('hidden text: ')
            except EOFError:
                return

        # transform and output the string
        output(Obscure.show(text, cmdline['--encoding']))


# Search {{{1
class Search(Command):
    NAMES = 'search', 's'
    DESCRIPTION = 'search accounts'
    USAGE = dedent("""
        Search for accounts whose values contain the search text.

        Usage:
            avendesora search <text>
            avendesora s      <text>
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(title=title(cls.DESCRIPTION), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # run the generator
        generator = PasswordGenerator()

        # search for accounts that match search criteria
        to_print = []
        for acct in generator.search_accounts(cmdline['<text>']):
            aliases = split(getattr(acct, 'aliases', []))

            aliases = ' (%s)' % (', '.join(aliases)) if aliases else ''
            to_print += [acct.get_name() + aliases]
        output(cmdline['<text>']+ ':')
        output('    ' + ('\n    '.join(sorted(to_print))))


# Value {{{1
class Value(Command):
    NAMES = 'value', 'val', 'v'
    DESCRIPTION = 'show an account value'
    USAGE = dedent("""
        Produce an account value. If the value is secret, it is produced only
        temporarily unless --stdout is specified.

        Usage:
            avendesora value [options] [--stdout | --clipboard] [<account> [<field>]]
            avendesora val   [options] [--stdout | --clipboard] [<account> [<field>]]
            avendesora v     [options] [--stdout | --clipboard] [<account> [<field>]]

        Options:
            -c, --clipboard         Write output to clipboard rather than stdout.
            -s, --stdout            Write output to the standard output without
                                    any annotation or protections.
            -v, --verbose           Add additional information to log file to
                                    help identify issues in account discovery.
            -t <title>, --title <title>
                                    Use account discovery on this title.
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(title=title(cls.DESCRIPTION), usage=cls.USAGE)

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
            account_name, script = generator.discover_account(
                title=cmdline['--title'], verbose=cmdline['--verbose']
            )
            account = generator.get_account(account_name)
            writer.run_script(account, script)


# Values {{{1
class Values(Command):
    NAMES = 'values', 'vals', 'V'
    DESCRIPTION = 'display all account values'
    USAGE = dedent("""
        Show all account values.

        Usage:
            avendesora values <account>
            avendesora vals   <account>
            avendesora V      <account>
    """).strip()

    @classmethod
    def help(cls):
        text = dedent("""
            {title}

            {usage}
        """).strip()
        return text.format(title=title(cls.DESCRIPTION), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # run the generator
        generator = PasswordGenerator()

        # determine the account
        account = generator.get_account(cmdline['<account>'])
        account.write_summary()

# Version {{{1
class Version(Command):
    NAMES = 'version',
    DESCRIPTION = 'display Avendesora version'
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
        return text.format(title=title(cls.DESCRIPTION), usage=cls.USAGE)

    @classmethod
    def run(cls, command, args):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        # output the version
        output('Avendesora version: %s' % __version__)

