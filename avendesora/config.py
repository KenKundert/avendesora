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
from .files import File
from .preferences import (
    BROWSERS, CHARSETS_MD5, CONFIG_FILENAME, DEFAULT_ARCHIVE_FILENAME,
    DEFAULT_BROWSER, DEFAULT_DISPLAY_TIME, DEFAULT_FIELD, DEFAULT_LOG_FILENAME,
    DEFAULT_VECTOR_FIELD, DICTIONARY_MD5, GPG_ARMOR, GPG_EXECUTABLE, GPG_HOME,
    REQUIRED_PROTOCOLS, SECRETS_MD5, SETTINGS_DIR, XDOTOOL_EXECUTABLE,
    XSEL_EXECUTABLE
)
from shlib import to_path
from inform import Error, warn
from textwrap import dedent
import re
from appdirs import user_config_dir

# Globals {{{1
Config = {}

# read_config() {{{1
def read_config():
    # First open the config file
    try:
        config_file = File(to_path(SETTINGS_DIR, CONFIG_FILENAME))
        contents = config_file.read()
        Config.update({k.lower(): v for k,v in contents.items()})
    except Error as err:
        #warn(err) # log() might be better, but log file is not available yet
        pass # config file is optional

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
        if name == 'dict_hash':
            return DICTIONARY_MD5
        if name == 'secrets_hash':
            return SECRETS_MD5
        if name == 'charsets_hash':
            return CHARSETS_MD5
        return default

# override_setting() {{{1
def override_setting(name, value):
    Config[name.lower()] = value
