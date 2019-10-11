# Account Files
#
# Loads account files either individually or en mass.
#
# Loading account files on demand makes Avendesora more responsive on most
# commands.
#
# Avendesora uses the manifests file, stored in configuration directory, to
# determine which file holds a particular account. This file contains a pickled
# manifests dictionary, which lists all account names and aliases contained in
# each account file. The account names and aliases are all hashed so it is not
# possible to know the names of the user's accounts by examining the manifests
# file. Once loaded the manifests mapping is inverted to create the account
# catalog, which maps account names hashes to file names.  The same thing is
# done for urls and titles in order to speed up loading the right accounts file
# when account discovery is used. With urls, the url is often a prefix, so along
# with each hash, the number of characters to match is included. The titles are
# glob strings and so cannot be hashed.

# License {{{1
# Copyright (C) 2016-18 Kenneth S. Kundert
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
from .account import Account, canonicalize
from .collection import Collection
from .config import get_setting
from .gpg import PythonFile
from .shlib import getmod, mkdir, rm
from .utilities import OSErrors
from cryptography.fernet import Fernet
from fnmatch import fnmatch
from inform import Error, comment, codicil, log, os_error, warn
from hashlib import sha256
from textwrap import dedent
from time import time
import base64
import pickle
import sys


# Globals {{{1
MANIFESTS_FILENAME = 'manifests'
if sys.version_info.major < 3:
    PICKLE_ARGS = dict()
else:
    PICKLE_ARGS = dict(encoding='utf8')


# AccountFiles class (private) {{{1
class AccountFiles:
    def __init__(self, warnings=True):  # {{{2
        # initialize object {{{3
        self.loaded = set()
        self.name_index = {}
        self.name_manifests = {}
        self.url_manifests = {}
        self.title_manifests = {}
        self.shared_secrets = {}
        self.existing_names = {}

        # check permissions, dates on account files {{{3
        most_recently_updated = 0
        mask = get_setting('account_file_mask')
        for filename in get_setting('accounts_files', []):
            path = get_setting('settings_dir') / filename
            resolved_path = path.resolve()

            # check file permissions
            permissions = getmod(resolved_path)
            violation = permissions & mask
            if violation:
                recommended = permissions & ~mask & 0o777
                warn("file permissions are too loose.", culprit=path)
                codicil("Recommend running: chmod {:o} {}".format(recommended, resolved_path))

            # determine time of most recently updated account file
            updated = resolved_path.stat().st_mtime
            if updated > most_recently_updated:
                most_recently_updated = updated

        # check for missing or stale archive file {{{3
        archive_file = get_setting('archive_file')
        if archive_file and warnings:
            if archive_file.exists():
                resolved_path = archive_file.resolve()

                # check file permissions
                permissions = getmod(resolved_path)
                violation = permissions & mask
                if violation:
                    recommended = permissions & ~mask & 0o777
                    warn("file permissions are too loose.", culprit=path)
                    codicil("Recommend running: chmod {:o} {}".format(
                        recommended, resolved_path)
                    )

                # warn user if archive file is out of date
                stale = float(get_setting('archive_stale'))
                archive_updated = resolved_path.stat().st_mtime
                if most_recently_updated > archive_updated:
                    log('Avendesora archive is {:.0f} hours out of date.'.format(
                        (most_recently_updated - archive_updated)/3600
                    ))
                    # archive_age = time() - archive_updated
                    account_age = time() - most_recently_updated
                    if account_age > 86400 * stale:
                        warn('stale archive.')
                        codicil(dedent("""\
                            Recommend running 'avendesora changed' to determine
                            which account entries have changed, and if all the
                            changes are expected, running 'avendesora archive'
                            to update the archive.
                        """), wrap=True)
                else:
                    log('Avendesora archive is up to date.')
            else:
                warn('archive missing.')
                codicil(
                    "Recommend running 'avendesora archive'",
                    "to create the archive."
                )

    def load_account_file(self, filename):  # {{{2
        if filename in self.loaded:
            return

        # read the file
        settings_dir = get_setting('settings_dir')
        path = settings_dir / filename
        account_file = PythonFile(path)
        contents = account_file.run()
        master_seed = contents.get('master_seed')
        if master_seed:
            self.shared_secrets[path.stem] = master_seed

        # traverse through all accounts and pass in fileinfo and master seed;
        # will be ignored if already set
        for account in Account.all_loaded_accounts():
            account.preprocess(master_seed, account_file, self.existing_names)

        self.loaded.add(filename)

    def load_account(self, name):  # {{{2
        canonical_name = canonicalize(name)
        self.read_manifests()
        if canonical_name in self.name_index:
            filename = self.name_index[canonical_name]
            self.load_account_file(filename)
            if canonical_name in Account._accounts:
                self.write_manifests()
                return
        # not in name_index, just read files until it is found
        for filename in get_setting('accounts_files', []):
            self.load_account_file(filename)
            if canonical_name in Account._accounts:
                break
        self.write_manifests()

    def load_account_files(self):  # {{{2
        for filename in get_setting('accounts_files', []):
            self.load_account_file(filename)
        self.write_manifests()

    def load_matching(self, title_components):  # {{{2
        self.read_manifests()
        found = False

        # load filenames that contain matching urls
        if 'host' in title_components:
            for filename, urls in self.url_manifests.items():
                for host, path, exact_path in urls:
                    if host != title_components['host']:
                        continue
                    if exact_path:
                        if path != title_components['path']:
                            continue
                    else:
                        if not title_components['path'].startswith(path):
                            continue
                    self.load_account_file(filename)
                    found = True

        # load filenames that contain matching titles
        title = title_components.get('rawtitle')
        if title:
            for filename, titles in self.title_manifests.items():
                for candidate in titles:
                    if fnmatch(title, candidate):
                        self.load_account_file(filename)
                        found = True

        # url/title not in cache (perhaps cache was missing), load everything
        if not found:
            self.load_account_files()

    def read_manifests(self):  # {{{2
        if self.name_index:
            return
        cache_dir = get_setting('cache_dir')
        manifests_path = cache_dir / MANIFESTS_FILENAME
        try:
            encrypted = manifests_path.read_bytes()

            user_key = get_setting('user_key')
            if not user_key:
                raise Error('no user key.')
            key = base64.urlsafe_b64encode(sha256(user_key.encode('ascii')).digest())
            fernet = Fernet(key)
            contents = fernet.decrypt(encrypted)

            try:
                cache = pickle.loads(contents, **PICKLE_ARGS)
                self.name_manifests = cache['names']
                self.url_manifests = cache['urls']
                self.title_manifests = cache['titles']

                # build the name_index by inverting the name_manifests
                self.name_index = {
                    h:n for n,l in self.name_manifests.items() for h in l
                }
            except (ValueError, pickle.UnpicklingError) as e:
                warn('garbled manifest.', culprit=manifests_path, codicil=str(e))
                manifests_path.unlink()
            assert isinstance(self.name_index, dict)
        except OSErrors as e:
            comment(os_error(e))

    def write_manifests(self):  # {{{2
        # do not modify existing name_index if no account files were loaded
        if not self.loaded:
            return
        log('Updating manifests.')
        name_manifests = self.name_manifests
        url_manifests = self.url_manifests
        title_manifests = self.title_manifests

        # remove entries for loaded files from name_index
        for filename in self.loaded:
            name_manifests[filename] = []
            url_manifests[filename] = []
            title_manifests[filename] = []

        # build name manifests
        for name, account in Account._accounts.items():
            filename = account._file_info.path.name
            name_manifests[filename].append(name)

        # build url and title manifests
        for account in Account.all_loaded_accounts():
            filename = account._file_info.path.name
            if filename not in self.loaded:
                # This should not occur, but if PasswordGenerator is
                # instantiated more than once, which should only occur in the
                # tests, then there could be accounts hanging around from
                # previous instantiations. Ignore them.
                continue
            discovery = getattr(account, 'discovery', ())

            # urls
            urls = []
            for each in Collection(discovery):
                for u in each.all_urls(components=True).values():
                    urls += u
            # urls is a list of triples, each triple consists of the host and
            # path components of the url, and a boolean indicating whether the
            # entire path must match.
            url_manifests[filename].extend(urls)

            # titles
            titles = []
            for each in Collection(discovery):
                for t in each.all_titles().values():
                    titles += t
            title_manifests[filename].extend(titles)

        # trip out the duplicates
        for filename in url_manifests:
            if filename in self.loaded:
                url_manifests[filename] = set(url_manifests[filename])
                title_manifests[filename] = set(title_manifests[filename])

        # write the manifests
        cache_dir = get_setting('cache_dir')
        manifests_path = cache_dir / MANIFESTS_FILENAME
        cache = dict(
            names=name_manifests, urls=url_manifests, titles=title_manifests
        )
        contents = pickle.dumps(cache)

        user_key = get_setting('user_key')
        key = base64.urlsafe_b64encode(sha256(user_key.encode('ascii')).digest())
        fernet = Fernet(key)
        encrypted = fernet.encrypt(contents)

        try:
            mkdir(cache_dir)
            manifests_path.write_bytes(encrypted)
        except OSError as e:
            warn(os_error(e))

    @staticmethod
    def delete_manifests():  # {{{2
        cache_dir = get_setting('cache_dir')
        manifests_path = cache_dir / MANIFESTS_FILENAME
        rm(manifests_path)
