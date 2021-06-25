# Password Generator

# License {{{1
# Copyright (C) 2016-2021 Kenneth S. Kundert
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
from .dictionary import Dictionary
from .error import PasswordError
from .files import AccountFiles
from .gpg import GnuPG, PythonFile, GPG_EXTENSIONS
from .obscure import Hidden
from .preferences import (
    CONFIG_DEFAULTS, NONCONFIG_SETTINGS, ACCOUNTS_FILE_INITIAL_CONTENTS,
    CONFIG_FILE_INITIAL_CONTENTS, CONFIG_DOC_FILE_INITIAL_CONTENTS,
    USER_KEY_FILE_INITIAL_CONTENTS, HASH_FILE_INITIAL_CONTENTS,
    STEALTH_ACCOUNTS_FILE_INITIAL_CONTENTS, ACCOUNT_LIST_FILE_CONTENTS,
)
from .script import Script
from .secrets import Passphrase
from .shlib import to_path, getmod, mv, rm
from .title import Title
from .utilities import generate_random_string
from inform import codicil, conjoin, log, os_error, render, warn, is_str
from textwrap import dedent, wrap
from pathlib import Path
import hashlib


# PasswordGenerator class{{{1
class PasswordGenerator(object):
    """Initializes the password generator.
    You should pass no arguments unless you are creating the user's Avendesora
    data directory.

    Once instantiated, you can use get_account() to load a specific account, or
    all_accounts() to load all accounts.

    Args:
        init (bool): Create user's directory.

        gpg_ids (list of strings):
            List of GPG identities to use when creating user's directory.

        check_integrity (bool):
            If true will validate that certain critical components in Avendesora
            have not be tampered with.  Checking the integrity can take up to a
            second, so recommend you pass False on interactive commands that
            benefit from low startup overhead and True on the more expensive
            commands to assure integrity is occasionally checked.

        warnings (bool):
            Suppress warnings from accounts. Useful when processing many
            accounts.  Does not affect warnings from the integrity check.

    Raises:
        :exc:`avendesora.PasswordError`:
            Indicates an issue opening the user's accounts.
    """

    # Constructor {{{2
    def __init__(
            self, init=False, gpg_ids=None, check_integrity=False, warnings=True
    ):
        # initialize avendesora (these should already be done if called from
        # main, but it is safe to call them again)
        read_config()
        GnuPG.initialize()

        # create the avendesora data directory
        if init:
            self._initialize(gpg_ids, init)
            return

        # check the integrity of avendesora
        if check_integrity:
            self._validate_components()

        # prepare to read accounts files
        self.account_files = AccountFiles(warnings)

    # _initialize() (private){{{2
    def _initialize(self, gpg_ids, filename):
        # If filename is True, this is being called as part of the Avendesora
        # 'initialize' command, in which case all missing files should be created.
        # If filename is a string, this is being called as part of the
        # Avendesora 'new' command, in which case a single new account file
        # should be created.
        def split(s, l=72):
            # Break long string into a series of adjacent shorter strings
            if len(s) < l:
                return '"%s"' % s
            chunks = ['    "%s"' % s[i:i+l] for i in range(0, len(s), l)]
            return '\n' + '\n'.join(chunks) + '\n'

        # create settings directory if it does not exist
        settings_dir = to_path(get_setting('settings_dir'))
        if not settings_dir.exists():
            settings_dir.mkdir(mode=0o700, parents=True)
            settings_dir.chmod(0o700)

        # Create dictionary of available substitutions for CONTENTS strings
        fields = {}
        for key in CONFIG_DEFAULTS:
            value = get_setting(key, expand=False)
            value = render(str(value) if isinstance(value, Path) else value)
            fields.update({key: value})
        for key in NONCONFIG_SETTINGS:
            value = get_setting(key, expand=False)
            value = render(str(value) if isinstance(value, Path) else value)
            fields.update({key: value})
        fields['encoding'] = get_setting('encoding')
            # get this one again, this time without the quotes
        gpg_ids = gpg_ids if gpg_ids else get_setting('gpg_ids', [])
        fields.update({
            'section': '{''{''{''1',
            'master_seed': split(Hidden.conceal(generate_random_string(72))),
            'user_key': split(Hidden.conceal(generate_random_string(72))),
            'gpg_ids': repr(' '.join(gpg_ids)),
        })

        # delete the config_doc_file so we always get an updated version.
        if (get_setting('config_doc_file')):
            try:
                rm(get_setting('config_doc_file'))
            except OSError as e:
                warn(os_error(e))

        # create the initial versions of the files in the settings directory
        if filename is True:
            path = to_path(get_setting('account_list_file'))
            if path.suffix in GPG_EXTENSIONS:
                raise PasswordError('encryption is not supported.', culprit=path)

            # Assure that the default initial set of files is present
            for path, contents in [
                (get_setting('config_file'), CONFIG_FILE_INITIAL_CONTENTS),
                (get_setting('config_doc_file'), CONFIG_DOC_FILE_INITIAL_CONTENTS),
                (get_setting('hashes_file'), HASH_FILE_INITIAL_CONTENTS),
                (get_setting('user_key_file'), USER_KEY_FILE_INITIAL_CONTENTS),
                (get_setting('default_accounts_file'), ACCOUNTS_FILE_INITIAL_CONTENTS),
                (get_setting('default_stealth_accounts_file'), STEALTH_ACCOUNTS_FILE_INITIAL_CONTENTS),
                (get_setting('account_list_file'), ACCOUNT_LIST_FILE_CONTENTS),
            ]:
                if path:
                    log('Creating initial version.', culprit=path)
                    f = PythonFile(path)
                    f.create(contents.format(**fields), gpg_ids)
                        # create will not overwrite an existing file, instead it
                        # reads the file.
        else:
            # Create a new accounts file
            fields['accounts_files'] = render(
                get_setting('accounts_files', []) + [filename]
            )
                # do not sort, the first file is treated special
            path = to_path(get_setting('settings_dir'), filename)
            if path.exists():
                raise PasswordError('exists.', culprit=path)
            if path.suffix in GPG_EXTENSIONS and not gpg_ids:
                raise PasswordError('Must specify GPG IDs.')
            log('Creating accounts file.', culprit=path)
            f = PythonFile(path)
            f.create(ACCOUNTS_FILE_INITIAL_CONTENTS.format(**fields), gpg_ids)

            # update the accounts list file
            path = to_path(
                get_setting('settings_dir'), get_setting('account_list_file')
            )
            log('Update accounts list.', culprit=path)
            f = PythonFile(path)
            try:
                mv(path, str(path) + '~')
                f.create(ACCOUNT_LIST_FILE_CONTENTS.format(**fields), gpg_ids)
            except OSError as e:
                raise PasswordError(os_error(e))

    # _validate_components() (private) {{{2
    def _validate_components(self):
        from pkg_resources import resource_filename

        # check permissions on the settings directory
        path = get_setting('settings_dir')
        mask = get_setting('config_dir_mask')
        try:
            permissions = getmod(path)
        except FileNotFoundError:
            raise PasswordError('missing, must run initialize.', culprit=path)
        violation = permissions & mask
        if violation:
            recommended = permissions & ~mask & 0o777
            warn("directory permissions are too loose.", culprit=path)
            codicil("Recommend running: chmod {:o} {}".format(recommended, path))

        # Check that files that are critical to the integrity of the generated
        # secrets have not changed
        for path, kind in [
            (to_path(resource_filename(__name__, 'secrets.py')), 'secrets_hash'),
            (to_path(resource_filename(__name__, 'charsets.py')), 'charsets_hash'),
            ('default', 'dict_hash'),
            ('mnemonic', 'mnemonic_hash'),
        ]:
            try:
                contents = path.read_text()
            except AttributeError:
                contents = '\n'.join(Dictionary(path).get_words())
            except OSError as e:
                raise PasswordError(os_error(e))
            md5 = hashlib.md5(contents.encode('utf-8')).hexdigest()
            # Check that file has not changed.
            if md5 != get_setting(kind):
                warn("file contents have changed.", culprit=path)
                lines = wrap(dedent("""\
                        This could result in passwords that are inconsistent with
                        those created in the past.  Use 'avendesora changed' to
                        assure that nothing has changed. Then, to suppress this
                        message, change {hashes} to contain:
                    """.format(hashes=get_setting('hashes_file'))
                ))
                lines.append("     {kind} = '{md5}'".format(kind=kind, md5=md5))
                codicil(*lines, sep='\n')

    # get_account() {{{2
    def get_account(self, name, request_seed=False, stealth_name=None):
        """Return a specific account.

        Args:
            name (str):
                Looks up an account by name and returns it. This name must match
                an account name or an account alias. The matching algorithm
                ignores case and treats dash and underscore as equivalent.
            request_seed (str or bool):
                If specified an additional seed is provided to the account (see:
                :ref:`misdirection <misdirection>`).  It may be specified as a
                string, in which case it is used as the seed.  Otherwise if
                true, the seed it requested directly from the user.
            stealth_name (str):
                The name used as the account name if the account is a stealth
                account.

        Returns:
            :class:`avendesora.Account`: An account. The class itself is
            returned, and not an instance of the class.

        Raises:
            :exc:`avendesora.PasswordError`:
                There is no account that matches the given name.
        """
        if not name:
            raise PasswordError('no account specified.')
        self.account_files.load_account(name)
        account = Account.get_account(name)
        account.initialize(request_seed, stealth_name)
        return account

    # get_value() {{{2
    def get_value(self, path, request_seed=False, stealth_name=None):
        """Get account value given path that includes account and field names.

        Args:
            path (str):
                Path includes account name and field name separated by a colon.
                Paths of the following forms are accepted:

                    |  *account*: account's default field
                    |  *account:name*: account and field name of a scalar value
                    |  *account:name.key* or *account:name[key]*:
                    |      member of a dictionary or array
                    |      key is string for dictionary, integer for array

            request_seed (str or bool):
                If specified an additional seed is provided to the account (see:
                :ref:`misdirection <misdirection>`).  It may be specified as a
                string, in which case it is used as the seed.  Otherwise if
                true, the seed it requested directly from the user.
            stealth_name (str):
                The name used as the account name if the account is a stealth
                account.

        Returns:
            :class:`avendesora.Account`: An account. The class itself is
            returned, and not an instance of the class.

        Raises:
            :exc:`avendesora.PasswordError`:
                There is no account of field that matches the given path.
        """
        name, _, field = path.partition(':')
        account = self.get_account(name, request_seed, stealth_name)
        return account.get_value(field)

    # discover_account() {{{2
    def discover_account(self, url=None, title=None, verbose=False):
        """Discover the account from the environment.

        Examine the environment and return the script that matches (the script
        is initialized, and so contains a pointer to the right account). If more
        than one account/secret matches, user is queried to resolve the
        ambiguity.

        Args:
            url (str):
                Specifying the URL short-circuits the processing of the
                title that is used to find the URL.

            title (str):
                Override the window title. This is used for debugging.

            verbose (bool):
                Run the discovery process in verbose mode (adds more information
                to log file that can help debug account discovery.

        Raises:
            :exc:`avendesora.PasswordError`:
                There is no account that matches the given environment.
        """
        log('Account Discovery ...')

        if not verbose:
            verbose = get_setting('verbose')

        # get and parse the title
        title_components = Title(url=url, override=title).get_data()

        # load candidate account files
        self.account_files.load_matching(title_components)

        # sweep through accounts to see if any recognize this title data
        matches = {}
        seen = set()
        for account in Account.all_loaded_accounts():
            name = account.get_name()
            if verbose:
                log('Trying:', name)
            for key, script in account.recognize(title_components, verbose):
                # identify and skip duplicates
                if (name, script) in seen:
                    continue
                seen.add((name, script))
                ident = '%s (%s)' % ((name, key) if key else (name, script))
                ident = '%s: %s' % (len(matches), ident)  # assure uniqueness
                matches[ident] = account, script
                log('%s matches' % ident)

        if not matches:
            msg = 'cannot find appropriate account.'
            raise PasswordError(msg)
        if len(matches) > 1:
            choice = show_list_dialog('Choose Secret', sorted(matches.keys()))
            if choice is None:
                raise PasswordError('user abort.')
            log('User selects %s' % choice)
            account, script = matches[choice]
        else:
            account, script = matches.popitem()[1]
                # this odd little piece of code gives the value of the one item in
                # the dictionary
        if script is True:
            # this bit of trickery gets the name of the default field
            n, k = account.split_field(None)
            script = "{%s}{return}" % account.combine_field(n, k)
        if is_str(script):
            script = Script(script)
        script.initialize(account)
        return script

    # all_accounts() {{{2
    def all_accounts(self):
        "Iterate through all accounts."
        self.account_files.load_account_files()
        for account in Account.all_loaded_accounts():
            yield account

    # find_acounts() {{{2
    def find_accounts(self, target):
        """Find accounts with names or aliases that contain a substring.

        Args:
            target (str): The desired substring.

        Returns:
            :class:`avendesora.Account`: Iterates through matching accounts.
        """
        for account in self.all_accounts():
            if account.id_contains(target):
                yield account

    # search_acounts() {{{2
    def search_accounts(self, target):
        """Find accounts with values that contain a substring.

        Args:
            target (str): The desired substring.

        Returns:
            :class:`avendesora.Account`: Iterates through matching accounts.
        """
        for account in self.all_accounts():
            if account.account_contains(target):
                yield account

    # challenge_response() {{{2
    def challenge_response(self, name, challenge):
        """Generate a response to a challenge.

        Given the name of a master seed (actually the basename of the file that
        contains the master seed), returns an identifying response to a
        challenge. If no challenge is provided, one is generated based on the
        time and date. Returns both the challenge and the expected response as a
        tuple.

        Args:
            name (str): The name of the master seed.
            challenge (str): The challenge (may be empty).
        """

        try:
            if not challenge:
                from arrow import utcnow
                now = str(utcnow())
                c = Passphrase()
                c.set_seeds([now])
                challenge = str(c)
            r = Passphrase()
            shared_secrets = self.account_files.shared_secrets
            r.set_seeds([shared_secrets[name], challenge])
            response = str(r)
            return challenge, response
        except KeyError:
            choices = conjoin(sorted(shared_secrets.keys()))
            raise PasswordError(
                'Unknown partner. Choose from %s.' % choices,
                culprit=name
            )
