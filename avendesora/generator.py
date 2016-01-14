from .preferences import (
    SETTINGS_DIR, CONFIG_FILENAME, CONFIG_FILE_INITIAL_CONTENTS,
    ACCOUNTS_FILE_INITIAL_CONTENTS
)
from .files import AccountFile
from .gpg import GPG
from .dictionary import DICTIONARY
from .account import Account
from messenger import Error, debug, terminate_if_errors
from shlib import Path

class PasswordGenerator:
    def __init__(self, init=False, gpg_id=None):
        self.gpg = GPG(gpg_id)
        self.active_account = None

        # First open the config file
        self.config = AccountFile(
            Path(SETTINGS_DIR, CONFIG_FILENAME),
            self.gpg,
            self,
            init,
            CONFIG_FILE_INITIAL_CONTENTS,
        )

        # Now open any accounts files found
        for filename in self.config.accounts_files:
            AccountFile(
                Path(SETTINGS_DIR, filename),
                self.gpg,
                self,
                init,
                ACCOUNTS_FILE_INITIAL_CONTENTS,
            )
        terminate_if_errors()

        DICTIONARY.validate(self.config.dict_hash)

    def activate_account(self, account):
        if not account:
            raise Error('no account specified.')
        for each in Account.all_accounts():
            if each.matches_exactly(account):
                each.initialize()
                self.active_account = each
                return
        raise Error('not found', culprit=account)

    def get_secret(self, secret=None):
        if not secret:
             secret = self.active_account.get_value('default')
        if not secret:
             secret = 'passcode'
        value = self.active_account.get_value(secret)
        if value:
            return value
        else:
            raise Error('not found', culprit=secret)

    def find_accounts(self, target):
        accounts = []
        for each in Account.all_accounts():
            if each.id_contains(target):
                accounts.append(each)
        return accounts

    def search_accounts(self, target):
        accounts = []
        for each in Account.all_accounts():
            if each.account_contains(target):
                accounts.append(each)
        return accounts

    def add_missing_master(self, master):
        for each in Account.all_accounts():
            if not hasattr(each, 'master'):
                each.master = master
