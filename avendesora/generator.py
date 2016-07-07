from .preferences import (
    SETTINGS_DIR, CONFIG_FILENAME, CONFIG_FILE_INITIAL_CONTENTS,
    ACCOUNTS_FILE_INITIAL_CONTENTS
)
from .files import AccountFile
from .gpg import GPG
from .dictionary import DICTIONARY
from .account import Account
from .title import Title
from inform import Error, debug, terminate_if_errors
from shlib import to_path
from urllib.parse import urlparse

class PasswordGenerator:
    def __init__(self, init=False, gpg_id=None):
        self.gpg = GPG(gpg_id)

        # First open the config file
        self.config = AccountFile(
            to_path(SETTINGS_DIR, CONFIG_FILENAME),
            self.gpg,
            self,
            init,
            CONFIG_FILE_INITIAL_CONTENTS,
        )

        # Now open any accounts files found
        for filename in self.config.accounts_files:
            AccountFile(
                to_path(SETTINGS_DIR, filename),
                self.gpg,
                self,
                init,
                ACCOUNTS_FILE_INITIAL_CONTENTS,
            )
        terminate_if_errors()

        DICTIONARY.validate(self.config.dict_hash)

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
        for account in Account.all_accounts():
            secret = account.recognize(data)
            if secret:
                return account.get_name(), secret
        raise Error('cannot find appropriate account.')

    def add_missing_master(self, master):
        for account in Account.all_accounts():
            if not hasattr(account, 'master'):
                account.master = master
