# Account Files
#
# Loads account files either individually or en mass while maintaining the
# catalog file, which keeps mappings between account names and the files that
# contain them. For privacy reasons, the catalog does not contain the account
# names, rather it contains their md5 hash.
#
# Loading account files on demand makes Avendesora more responsive on most
# commands. With 14 encrypted accounts files the run time for the value command
# was up around 4 seconds. By only loading one of the accounts files, I got that
# down to around 2 seconds. I measured the time it took to run Avendesora when
# the first statement in main() raised SystemExit, and the time required to run
# was 1.5 - 2 seconds. Furthermore, time required to run value command was 250ms
# whereas time required to run changed command was 2.9 seconds. So little is to
# be gained by further optimizing the time required to access a single account.
# Further attention should be focused on reducing start up time.

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
from .config import get_setting
from .error import PasswordError
from .gpg import PythonFile
from .shlib import getmod
from .utilities import OSErrors
from inform import comment, codicil, log, os_error, warn
from hashlib import md5
from textwrap import dedent, fill
from time import time
import pickle
import sys


# Globals {{{1
MANIFESTS_FILENAME = 'manifests'
if sys.version_info.major < 3:
    PICKLE_ARGS = dict()
else:
    PICKLE_ARGS = dict(encoding='utf8')



# Account Files class {{{1
class AccountFiles:

    def __init__(self, warnings=True):
        self.loaded = set()
        self.catalog = {}
        self.shared_secrets = {}
        self.existing_names = {}

        # check permissions, dates on account files
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
                codicil("Recommend running 'chmod {:o} {}'.".format(recommended, resolved_path))

            # determine time of most recently updated account file
            updated = resolved_path.stat().st_mtime
            if updated > most_recently_updated:
                most_recently_updated = updated

        # check for missing or stale archive file
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
                    codicil("Recommend running 'chmod {:o} {}'.".format(recommended, resolved_path))

                # warn user if archive file is out of date
                stale = float(get_setting('archive_stale'))
                archive_updated = resolved_path.stat().st_mtime
                if most_recently_updated > archive_updated:
                    log('Archive is up-to-date.')
                    age_in_seconds = time() - most_recently_updated
                    if age_in_seconds > 86400 * stale:
                        warn('stale archive.')
                        codicil(fill(dedent("""
                            Recommend running 'avendesora changed' to determine
                            which account entries have changed, and if all the
                            changes are expected, running 'avendesora archive' to
                            update the archive.
                        """).strip()))
                else:
                    log('Archive is out of date.')
            else:
                warn('archive missing.')
                codicil(
                    "Recommend running 'avendesora archive'",
                    "to create the archive."
                )

    def load_account_file(self, filename):
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
        for account in Account.all_accounts():
            account.preprocess(master_seed, account_file, self.existing_names)

        self.loaded.add(filename)

    def load_account(self, name):
        canonical_name = canonicalize(name)
        self.read_manifests()
        hash = md5(canonical_name.encode('utf8')).digest()
        if hash in self.catalog:
            filename = self.catalog[hash]
            self.load_account_file(filename)
            assert canonical_name in Account._accounts
        else:
            # not in catalog, just read files until it is found
            for filename in get_setting('accounts_files', []):
                self.load_account_file(filename)
                if canonical_name in Account._accounts:
                    return
        self.write_manifests()

    def load_account_files(self):
        for filename in get_setting('accounts_files', []):
            self.load_account_file(filename)
        self.write_manifests()

    def read_manifests(self):
        if self.catalog:
            return
        settings_dir = get_setting('settings_dir')
        manifests_path = settings_dir / MANIFESTS_FILENAME
        try:
            contents = manifests_path.read_bytes()
            try:

                manifests = pickle.loads(contents, **PICKLE_ARGS)
                # build the catalog by inverting the manifests
                self.catalog = {
                    h:n for n,l in manifests.items() for h in l
                }
            except (ValueError, pickle.UnpicklingError) as e:
                warn('garbled manifest.', culprit=manifests_path, codicil=str(e))
            assert isinstance(self.catalog, dict)
        except OSErrors as e:
            comment(os_error(e))

    def write_manifests(self):
        # do not modify existing catalog if no account files were loaded
        if not self.loaded:
            return
        log('Updating manifests.')

        # remove entries from catalog from loaded files
        if self.catalog:
            for k in self.catalog.keys():
                if k in self.loaded:
                    del self.catalog[k]

        # now add back the updated entries
        for name, account in Account._accounts.items():
            hash = md5(name.encode('utf8')).digest()
            self.catalog[hash] = account._file_info.path.name

        # build manifests by inverting the catalog
        manifests = {n:[] for n in get_setting('accounts_files', [])}
        for k, v in self.catalog.items():
            manifests[v].append(k)

        # write the manifests
        settings_dir = get_setting('settings_dir')
        manifests_path = settings_dir / MANIFESTS_FILENAME
        contents = pickle.dumps(manifests)

        try:
            manifests_path.write_bytes(contents)
        except OSError as e:
            warn(os_error(e))
