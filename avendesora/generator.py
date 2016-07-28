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
from .conceal import Hidden
from .config import read_config, get_setting
from .dialog import show_list_dialog
from .gpg import GnuPG, File
from .preferences import (
    CONFIG_DEFAULTS, NONCONFIG_SETTINGS, ACCOUNTS_FILE_INITIAL_CONTENTS,
    CONFIG_FILE_INITIAL_CONTENTS, USER_KEY_FILE_INITIAL_CONTENTS,
    HASH_FILE_INITIAL_CONTENTS, TEMPLATES_FILE_INITIAL_CONTENTS,
)
from .title import Title
from .utilities import generate_random_string, validate_componenets
from inform import debug, Error, fatal, log, terminate, terminate_if_errors
from shlib import to_path
from pathlib import Path
from urllib.parse import urlparse

# PasswordGenerator class{{{1
class PasswordGenerator:
    def __init__(self, init=False, gpg_id = None):
        # initialize avendesora (these should already be done if called from 
        # main, but it is safe to call them again)
        read_config()
        self.gpg = GnuPG.initialize(gpg_id)

        # check the integrity of avendesora
        validate_componenets()
        if init:
            self.initialize()
            terminate()

        # Now open any accounts files found
        for filename in get_setting('accounts_files', []):
            try:
                path = to_path(get_setting('settings_dir'), filename)
                account_file = File(path, self.gpg)
                contents = account_file.read()
                if 'master_password' in contents:
                    self.add_master_to_accounts(contents['master_password'])
                self.add_file_info_to_accounts(account_file)
            except Error as err:
                err.terminate()
        terminate_if_errors()

    def initialize(self):
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
            value = get_setting(key)
            value = repr(str(value) if isinstance(value, Path) else value)
            fields.update({key: value})
        for key in NONCONFIG_SETTINGS:
            value = get_setting(key)
            value = repr(str(value) if isinstance(value, Path) else value)
            fields.update({key: value})
        fields.update({
            'section': '{''{''{''1',
            'master_password': split(Hidden.conceal(generate_random_string(72))),
            'user_key': split(Hidden.conceal(generate_random_string(72))),
        })

        # create the initial versions of the files in the settings directory
        for path, contents in [
            (get_setting('config_file'), CONFIG_FILE_INITIAL_CONTENTS),
            (get_setting('hashes_file'), HASH_FILE_INITIAL_CONTENTS),
            (get_setting('user_key_file'), USER_KEY_FILE_INITIAL_CONTENTS),
            (get_setting('default_accounts_file'), ACCOUNTS_FILE_INITIAL_CONTENTS),
            (get_setting('default_templates_file'), TEMPLATES_FILE_INITIAL_CONTENTS),
        ]:
            if path:
                log('creating initial version.', culprit=path)
                f = File(path, self.gpg)
                f.create(contents.format(**fields))

    def get_account(self, name):
        if not name:
            raise Error('no account specified.')
        for account in Account.all_accounts():
            if account.matches_exactly(name):
                account.initialize()
                return account
        raise Error('not found.', culprit=name)

    def find_accounts(self, target):
        accounts = []
        for account in Account.all_accounts():
            if account.id_contains(target):
                accounts.append(account)
        return accounts

    def search_accounts(self, target):
        accounts = []
        for account in Account.all_accounts():
            if account.account_contains(target):
                accounts.append(account)
        return accounts

    def discover_account(self):
        # get and parse the title
        data = Title().get_data()

        # split the url into basic components if found
        url = data.get('url')
        if url:
            url = urlparse(url)
            data['protocol'] = url.scheme
            data['host'] = url.netloc
            data['path'] = url.path

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
            secret = account.recognize(data)
            if secret:
                matches[account.get_name()] = secret

        if not matches:
            msg = 'cannot find appropriate account.'
            log(msg)
            raise Error(msg)
        if len(matches) > 1:
            choice = show_list_dialog(sorted(matches.keys()))
            return choice, matches[choice]
        else:
            return matches.popitem()

    def add_master_to_accounts(self, master):
        for account in Account.all_accounts():
            if not hasattr(account, 'master'):
                account.master = master

    def add_file_info_to_accounts(self, file_info):
        for account in Account.all_accounts():
            if not hasattr(account, '_file_info'):
                account._file_info = file_info
