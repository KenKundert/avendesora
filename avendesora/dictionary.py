# Passphrase Dictionary
#
# Interfaces to the passphrase dictionary (the dictionary acts as the alphabet
# used to create pass phrases).

# License {{{1
# Copyright (C) 2013-17 Kenneth S. Kundert and Kale Kundert
#
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
from .config import get_setting
from shlib import to_path
from inform import error, os_error
import hashlib


class Dictionary(object):
    """Read Dictionary"""
    def __init__(self, path):
        # find the dictionary, initially look in the settings directory
        if not path.exists():
            # if not there look in install directory
            from pkg_resources import resource_filename
            path = to_path(resource_filename(__name__, 'words'))

        # open the dictionary
        try:
            contents = path.read_text()
        except OSError as e:
            error(os_error(e))
            contents = ''

        self.hash = hashlib.md5(contents.encode('utf-8')).hexdigest()
        self.words = contents.split()

DICTIONARY = Dictionary(get_setting('dictionary_file'))

# vim: set sw=4 sts=4 et:
