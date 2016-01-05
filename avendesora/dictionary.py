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
from scripts import join, head, isreadable, exists
from .preferences import SETTINGS_DIR, DICTIONARY_FILENAME, CONFIG_FILENAME
from messenger import display, error, os_error
from textwrap import wrap
import hashlib


class Dictionary:
    """Read Dictionary"""
    def __init__(self, filename, settings_dir):
        path = self._find_dictionary(filename, settings_dir)
        self.path = path
        contents = self._read_dictionary()
        self.hash = hashlib.sha1(contents.encode('utf-8')).hexdigest()
        self.words = contents.split()

    def _find_dictionary(self, filename, settings_dir):
        """Find Dictionary

        Finds the file that contains the dictionary of words used to construct
        pass phrases. Initially looks in the settings directory, if not there
        look in install directory.
        """
        path = join(settings_dir, filename)
        #if not exists(path):
        #    path = join(head(__file__), filename)
        if not exists(path):
            path = join(head(__file__), join('..', filename))
        if not isreadable(path):
            error("cannot open dictionary.", culprit=path)
        return path

    def _read_dictionary(self):
        """Read Dictionary"""
        try:
            with open(self.path) as f:
                return f.read()
        except IOError as err:
            error(os_error(err))
            return ''

    def validate(self, saved_hash):
        """Validate Dictionary"""
        if saved_hash != self.hash:
            display("Warning: '%s' has changed." % self.path)
            display("    " + "\n    ".join(wrap(' '.join([
                "This results in pass phrases that are inconsistent",
                "with those created in the past.",
                "Use 'abraxas --changed' to assure that nothing has changed",
                "and then update 'dict_hash' in %s/%s to %s." % (
                    SETTINGS_DIR, CONFIG_FILENAME, self.hash)
            ]))))

    # get_words
    def get_words(self):
        """Get the Words"""
        return self.words

DICTIONARY = Dictionary(DICTIONARY_FILENAME, SETTINGS_DIR)
# vim: set sw=4 sts=4 et:
