# Avendesora Password Generator Preferences
#
# Copyright (C) 2016 Kenneth S. Kundert

# License {{{1
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
from .files import AccountFile
from .preferences import (
    DEFAULT_LOG_FILENAME, DEFAULT_ARCHIVE_FILENAME, DEFAULT_FIELD,
    DEFAULT_VECTOR_FIELD, DEFAULT_DISPLAY_TIME, XDOTOOL_EXECUTABLE,
    XSEL_EXECUTABLE, GPG_EXECUTABLE, GPG_HOME, GPG_ARMOR, BROWSERS,
    DEFAULT_BROWSER, REQUIRED_PROTOCOLS, SETTINGS_DIR, CONFIG_FILENAME
)
from shlib import to_path
from inform import Error, log
from textwrap import dedent
import re
from appdirs import user_config_dir

# Globals {{{1
Config = {}

# read_config() {{{1
def read_config():
    # First open the config file
    try:
        config = AccountFile(to_path(SETTINGS_DIR, CONFIG_FILENAME))
        Config.update({k.lower(): v for k,v in config.contents.items()})
    except Error as err:
        log(err)

# get_setting() {{{1
def get_setting(name, default=None):
    name = name.lower()
    try:
        return Config[name]
    except KeyError:
        if name == 'log_file':
            return DEFAULT_LOG_FILENAME
        if name == 'archive_file':
            return DEFAULT_ARCHIVE_FILENAME
        if name == 'default_field':
            return DEFAULT_FIELD
        if name == 'default_vector_field':
            return DEFAULT_VECTOR_FIELD
        if name == 'display_time':
            return DEFAULT_DISPLAY_TIME
        if name == 'xdotool_executable':
            return XDOTOOL_EXECUTABLE
        if name == 'xsel_executable':
            return XSEL_EXECUTABLE
        if name == 'gpg_executable':
            return GPG_EXECUTABLE
        if name == 'gpg_home':
            return GPG_HOME
        if name == 'gpg_armor':
            return GPG_ARMOR
        if name == 'browsers':
            return BROWSERS
        if name == 'default_browser':
            return DEFAULT_BROWSER
        if name == 'required_protocols':
            return REQUIRED_PROTOCOLS
        return default
