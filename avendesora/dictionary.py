# Passphrase Dictionary
#
# Interfaces to the passphrase dictionary (the dictionary acts as the alphabet
# used to create pass phrases).
#
# Copyright (C) 2013-14 Kenneth S. Kundert and Kale Kundert

# License (fold)
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

# Imports (folds)
from .preferences import SETTINGS_DIR, DICTIONARY_FILENAME, CONFIG_FILENAME
from shlib import to_path
from inform import codicil, error, warn, os_error
from textwrap import dedent, wrap
import hashlib


class Dictionary:
    """Read Dictionary"""
    def __init__(self, filename, settings_dir):
        # find the dictionary, initially look in the settings directory
        path = to_path(settings_dir, filename)
        if not path.exists():
            # if not there look in install directory
            from pkg_resources import resource_filename
            path = to_path(resource_filename(__name__, 'words'))

        # open the dictionary
        try:
            contents= path.read_text()
        except OSError as err:
            error(os_error(err))
            contents = ''

        self.hash = hashlib.sha1(contents.encode('utf-8')).hexdigest()
        self.words = contents.split()

    def validate(self, saved_hash):
        """Validate Dictionary"""
        if saved_hash != self.hash:
            if not self.hash:
                # there is no dictionary and the user has already been informed
                return
            warn("dictionary has changed.")
            codicil(
                *wrap(dedent("""\
                    This results in pass phrases that are inconsistent
                    with those created in the past.  Use 'avendesora --changed' 
                    to assure that nothing has changed and then update 
                    'dict_hash' in {settings}/{config} to {hash}.
                """.format(
                    settings=SETTINGS_DIR,
                    config=CONFIG_FILENAME,
                    hash=self.hash
                ))), sep='\n'
            )

DICTIONARY = Dictionary(DICTIONARY_FILENAME, SETTINGS_DIR)
# vim: set sw=4 sts=4 et:
