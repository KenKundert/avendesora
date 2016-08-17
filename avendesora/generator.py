# Password Generator

# License {{{1
# Copyright (C) 2016 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/.


# Imports {{{1
from .account import Account
from .config import read_config, get_setting
from .dialog import show_list_dialog
from .gpg import GnuPG, PythonFile, GPG_EXTENSIONS
from .obscure import Hidden
from .preferences import (
    CONFIG_DEFAULTS, NONCONFIG_SETTINGS, ACCOUNTS_FILE_INITIAL_CONTENTS,
    CONFIG_FILE_INITIAL_CONTENTS, USER_KEY_FILE_INITIAL_CONTENTS,
    HASH_FILE_INITIAL_CONTENTS, STEALTH_ACCOUNTS_FILE_INITIAL_CONTENTS,
    ACCOUNT_LIST_FILE_CONTENTS,
)
from .title import Title
from .utilities import generate_random_string, validate_componenets, to_python
from inform import debug, Error, notify, log, terminate, terminate_if_errors
from shlib import to_path
from pathlib import Path
from urllib.parse import urlparse

# PasswordGenerator class{{{1
class PasswordGenerator:

    # Constructor {{{2
    def __init__(self, init=False, gpg_ids=None):
        # initialize avendesora (these should already be done if called from 
        # main, but it is safe to call them again)
        read_config()
        GnuPG.initialize()

        # check the integrity of avendesora
        validate_componenets()

        # create the avendesora data directory
        if init:
            self.initialize(gpg_ids, init)
            terminate()

        # Now open any accounts files found
        for filename in get_setting('accounts_files', []):
            try:
                path = to_path(get_setting('settings_dir'), filename)
                account_file = PythonFile(path)
                contents = account_file.run()
                if 'master_password' in contents:
                    self.add_master_to_accounts(contents['master_password'])
                self.add_file_info_to_accounts(account_file)
            except Error as err:
                err.terminate()
        terminate_if_errors()

    # initialize() {{{2
    def initialize(self, gpg_ids, filename):
        def split(s, l=72):
            # Break long string into a series of adjacent shorter strings
            if len(s) < l:
                return '"%s"' % s
            chunks = ['    "%s"' % s[i:i+l] for i in range(0, len(s), l)]
            return '\n' + '\n'.join(chunks) + '\n'

        def dict_to_str(d):
            lines = ['{']
            for k in sorted(d):
                lines.append("    '%s': '%s'," % (k, d[k]))
            lines.append('}')
            return '\n'.join(lines)

        # Create dictionary of available substitutions for CONTENTS strings
        fields = {}
        for key in CONFIG_DEFAULTS:
            value = get_setting(key, expand=False)
            value = to_python(str(value) if isinstance(value, Path) else value)
            fields.update({key: value})
        for key in NONCONFIG_SETTINGS:
            value = get_setting(key, expand=False)
            value = to_python(str(value) if isinstance(value, Path) else value)
            fields.update({key: value})
        gpg_ids = gpg_ids if gpg_ids else get_setting('gpg_ids', [])
        fields.update({
            'section': '{''{''{''1',
            'master_password': split(Hidden.conceal(generate_random_string(72))),
            'master_password2': split(Hidden.conceal(generate_random_string(72))),
            'user_key': split(Hidden.conceal(generate_random_string(72))),
            'gpg_ids': repr(' '.join(gpg_ids)),
        })

        # create the initial versions of the files in the settings directory
        if filename is True:
            # Assure that the default initial set of files is present
            for path, contents in [
                (get_setting('config_file'), CONFIG_FILE_INITIAL_CONTENTS),
                (get_setting('hashes_file'), HASH_FILE_INITIAL_CONTENTS),
                (get_setting('user_key_file'), USER_KEY_FILE_INITIAL_CONTENTS),
                (get_setting('default_accounts_file'), ACCOUNTS_FILE_INITIAL_CONTENTS),
                (get_setting('default_stealth_accounts_file'), STEALTH_ACCOUNTS_FILE_INITIAL_CONTENTS),
            ]:
                if path:
                    log('creating initial version.', culprit=path)
                    f = PythonFile(path)
                    f.create(contents.format(**fields), gpg_ids)
        else:
            # Create a new accounts file
            fields['accounts_files'] = get_setting('accounts_files', []) + [filename]
            path = to_path(get_setting('settings_dir'), filename)
            if path.exists():
                raise Error('exists.', culprit=path)
            if path.suffix in GPG_EXTENSIONS and not gpg_ids:
                raise Error('Must specify GPG IDs.')
            log('creating accounts file.', culprit=path)
            f = PythonFile(path)
            f.create(ACCOUNTS_FILE_INITIAL_CONTENTS.format(**fields), gpg_ids)

        # Create a new accounts file
        path = to_path(get_setting('account_list_file'))
        if path.suffix in GPG_EXTENSIONS:
            raise Error('encryption is not supported.', culprit=path)
        try:
            log('writing.', culprit=path)
            path.write_text(ACCOUNT_LIST_FILE_CONTENTS.format(**fields))
        except OSError as err:
            raise Error(os_error(err))

    # all_accounts() {{{2
    def all_accounts(self):
        for account in Account.all_accounts():
            yield account

    # get_acount() {{{2
    def get_account(self, name):
        if not name:
            raise Error('no account specified.')
        for account in Account.all_accounts():
            if account.matches_exactly(name):
                account.initialize()
                return account
        raise Error('not found.', culprit=name)

    # find_acounts() {{{2
    def find_accounts(self, target):
        accounts = []
        for account in Account.all_accounts():
            if account.id_contains(target):
                accounts.append(account)
        return accounts

    # search_acounts() {{{2
    def search_accounts(self, target):
        accounts = []
        for account in Account.all_accounts():
            if account.account_contains(target):
                accounts.append(account)
        return accounts

    # discover_account() {{{2
    def discover_account(self, title=None, verbose=False):
        log('Account Discovery ...')

        # get and parse the title
        data = Title(override=title).get_data()

        # sweep through accounts to see if any recognize this title data
        # recognizer may fund the following fields in data:
        #     rawdata: the original title
        #     title: the processed title
        #     url: the full url
        #     browser: the name of the browser
        #     protocol: the url scheme (ex. http, https, ...)
        #     host: the url host name or IP address
        #     path: the path component of the url
        #           does not include options or anchor
        matches = {}
        for account in Account.all_accounts():
            name = account.get_name()
            if verbose:
                log('Trying:', name)
            for key, script in account.recognize(data, verbose):
                ident = '%s (%s)' % (name, key) if key else name
                matches[ident] = name, script
                if verbose:
                    log('    %s matches' % ident)

        if not matches:
            msg = 'cannot find appropriate account.'
            notify(msg)
            raise Error(msg)
        if len(matches) > 1:
            choice = show_list_dialog(sorted(matches.keys()))
            return matches[choice]
        else:
            return matches.popitem()[1]

    # add_master_to_accounts() {{{2
    def add_master_to_accounts(self, master):
        for account in Account.all_accounts():
            if hasattr(account, 'master'):
                continue
            if hasattr(account, '_%s__NO_MASTER' % account.__name__):
                continue
            account.master = master

    # add_file_info_to_accounts() {{{2
    def add_file_info_to_accounts(self, file_info):
        for account in Account.all_accounts():
            # _file_info is used (as opposed to file_info) to prevent this 
            # attribute from being displayed by showall.
            if not hasattr(account, '_file_info'):
                account._file_info = file_info
