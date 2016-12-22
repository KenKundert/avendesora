# Avendesora Password Generator Settings
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
from .preferences import CONFIG_DEFAULTS, NONCONFIG_SETTINGS
from shlib import to_path
from inform import Error, comment, warn, is_str
from textwrap import dedent
import re
from appdirs import user_config_dir

# Globals {{{1
Config = {}

# read_config() {{{1
def read_config():
    if Config.get('READ'):
        return  # already read

    # First open the config file
    from .gpg import PythonFile
    path = get_setting('config_file')
    assert path.suffix.lower() not in ['.gpg', '.asc']
    config_file = PythonFile(path)
    if not config_file.exists():
        # have not yet initialized this account
        return
    try:
        contents = config_file.run()
        for k, v in contents.items():
            if k.startswith('_'):
                continue
            if k not in CONFIG_DEFAULTS:
                warn('%s: unknown.' % k, culprit=config_file)
                continue
            if k.endswith('_executable'):
                argv = v.split() if is_str(v) else list(v)
                path = to_path(argv[0])
                if not path.is_absolute():
                    warn(
                        'should use absolute path for executables.',
                        culprit=(config_file, k)
                    )
            Config[k] = v
        Config['READ'] = True
    except Error as err:
        comment('not found.', culprit=config_file)

    # Now open the hashes file
    hashes_file = PythonFile(get_setting('hashes_file'))
    try:
        contents = hashes_file.run()
        Config.update({k.lower(): v for k,v in contents.items()})
    except Error as err:
        pass

    # Now open the account list file
    account_list_file = PythonFile(get_setting('account_list_file'))
    try:
        contents = account_list_file.run()
        Config.update({k.lower(): v for k,v in contents.items()})
    except Error as err:
        pass

    # initilize GPG
    from .gpg import GnuPG
    GnuPG.initialize()

    # Now read the user key file
    user_key_file = get_setting('user_key_file')
    if user_key_file:
        user_key_file = PythonFile(get_setting('user_key_file'))
        try:
            contents = user_key_file.run()
            Config.update({k.lower(): v for k,v in contents.items()})
        except Error as err:
            pass

def add_setting(name, default):
    CONFIG_DEFAULTS[name] = default

# get_setting() {{{1
def get_setting(name, default=None, expand=True):
    name = name.lower()
    try:
        value = Config[name]
    except KeyError:
        try:
            value = CONFIG_DEFAULTS[name]
        except KeyError:
            try:
                value = NONCONFIG_SETTINGS[name]
            except KeyError:
                return default
    if value is None:
        return default
    if name == 'gpg_ids':
        value = value.split() if is_str(value) else value
    elif expand and name.endswith('_file'):
        value = to_path(get_setting('settings_dir'), value)
    return value

# override_setting() {{{1
def override_setting(name, value):
    Config[name.lower()] = value
