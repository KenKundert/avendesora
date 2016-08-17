# Account
# API for an account

# License {{{1
# Copyright (C) 2016 Kenneth S. Kundert
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
from .browsers import StandardBrowser
from .config import get_setting
from .obscure import Obscure
from .preferences import TOOL_FIELDS
from .recognize import Recognizer
from .secrets import Secret
from .utilities import items, values, split
from inform import (
    Color, conjoin, Error, is_collection, is_str, log, output, warn,
)
from textwrap import indent, dedent
from urllib.parse import urlparse
import re
import sys


# Globals {{{1
VECTOR_PATTERN = re.compile(r'\A(\w+)\[(\w+)\]\Z')
LabelColor = Color(
    color=get_setting('label_color'),
    scheme=get_setting('color_scheme'),
    enable=Color.isTTY()
)

# Account class {{{1
class Account:
    __NO_MASTER = True
        # prevents master password from being added to this base class

    # all_accounts() {{{2
    @classmethod
    def all_accounts(cls):
        for sub in cls.__subclasses__():
            yield sub
            for each in sub.all_accounts():
                yield each

    # fields() {{{2
    @classmethod
    def fields(cls):
        for key, value in cls.__dict__.items():
            if not key.startswith('_'):
                yield key, value

    # get_name() {{{2
    @classmethod
    def get_name(cls):
        try:
            return cls.NAME
        except AttributeError:
            # consider converting lower to upper case transitions in __name__ to
            # dashes.
            return cls.__name__.lower()

    # get_seed() {{{2
    @classmethod
    def get_seed(cls):
        try:
            return cls.seed
        except AttributeError:
            return cls.get_name()

    # matches_exactly() {{{2
    @classmethod
    def matches_exactly(cls, account):
        if account == cls.get_name():
            return True
        try:
            if account in split(cls.aliases):
                return True
        except AttributeError:
            pass
        return False

    # id_contains() {{{2
    @classmethod
    def id_contains(cls, target):
        target = target.lower()
        if target in cls.get_name().lower():
            return True
        try:
            for alias in split(cls.aliases):
                if target in alias.lower():
                    return True
        except AttributeError:
            pass
        return False

    # account_contains() {{{2
    @classmethod
    def account_contains(cls, target):
        if cls.id_contains(target):
            return True
        target = target.lower()
        for key, value in cls.fields():
            if key in TOOL_FIELDS:
                continue
            try:
                if is_collection(value):
                    for k, v in items(value):
                        if target in v.lower():
                            return True
                elif target in value.lower():
                    return True
            except AttributeError:
                # is not a string, and so 
                pass
        return False

    # recognize() {{{2
    @classmethod
    def recognize(cls, data, verbose):
        # try the specified recognizers
        discovery = getattr(cls, 'discovery', ())
        for recognizer in values(discovery):
            if isinstance(recognizer, Recognizer):
                script = recognizer.match(data, cls, verbose)
                name = getattr(recognizer, 'name', None)
                if script:
                    yield name, script
        if discovery:
            return

        # If no recognizers specified, just check the urls
        for url in split(cls.get_field('urls', default=[])):
            components = urlparse(url)
            protocol = components.scheme
            host = components.netloc
            if host == data.get('host'):
                if (
                    protocol != data.get('protocol') and
                    data['protocol'] in get_setting('required_protocols')
                ):
                    msg = 'url matches, but uses wrong protocol.'
                    notify(msg)
                    raise Error(msg, culprit=account.get_name())
                else:
                    yield None, True
                    return

    # initialize() {{{2
    @classmethod
    def initialize(cls):
        log('initializing', cls.get_name())
        try:
            if cls.master.is_secure():
                if not cls._file_info.encrypted:
                    warn(
                        'high value master password not contained in encrypted',
                        'account file.', culprit=cls.get_name()
                    )
        except AttributeError as err:
            pass

    # items() {{{2
    @classmethod
    def items(cls):
        for key in sorted(cls.__dict__):
            if not key.startswith('_'):
                yield key, cls.__dict__[key]

    # get_field() {{{2
    @classmethod
    def get_field(cls, name, key=None, default=False):
        """Get Field Value

        Return value from the account given a field name and key.
        """
        value = cls.__dict__.get(name)
        if value is None:
            if default is False:
                raise Error(
                    'not found.',
                    culprit=(cls.get_name(), cls.combine_name(name, key))
                )
            else:
                return default

        if key is None:
            if is_collection(value):
                raise Error(
                    'composite value found, need key.',
                    culprit=name,
                    is_collection=True,
                    collection = value
                )
        else:
            try:
                if is_collection(value):
                    value = value[key]
                else:
                    warn('not a composite value, key ignored.', culprit=name)
                    key = None
            except (IndexError, KeyError, TypeError):
                raise Error('not found.', culprit=cls.combine_name(name, key))

        # generate the value if needed
        try:
            value.generate(name, key, cls)
        except AttributeError as err:
            pass
        return value

    # is_secret() {{{2
    @classmethod
    def is_secret(cls, name, key=None):
        value = cls.__dict__.get(name)
        if key is None:
            return hasattr(value, 'generate')
        else:
            try:
                return hasattr(value[key], 'generate')
            except (IndexError, KeyError, TypeError):
                raise Error('not found.', culprit=cls.combine_name(name, key))

    # split_name() {{{2
    @classmethod
    def split_name(cls, name):
        # Account fields can either be scalars or composites (vectors or
        # dictionaries). This function takes a string (name) that the user
        # provides to specify which account value they wish and splits it into a
        # field name and a key.  If the field is a scalar, the key will be None.
        # Users request a value using one of the following forms:
        #     True: use default name
        #     field: scalar value (key=None)
        #     index: questions (field->'questions', key=index)
        #     field[index] or field/index: for vector value
        #     field[key] or field/key: for dictionary value

        if name is True or not name:
            name = cls.get_field('default', default=None)
        if not name:
            name = get_setting('default_field')

        # convert dashes to underscores
        name = str(name).replace('-', '_')

        # If name is an integer, treat it as number of security question.
        try:
            return get_setting('default_vector_field'), int(name)
        except ValueError:
            pass

        # Split name if given in the form: name/key
        try:
            name, key = name.split('.')
            try:
                return name, int(key)
            except ValueError:
                return name, key
        except ValueError:
            pass

        # Split name if given in the form: name[key]
        match = VECTOR_PATTERN.match(name)
        if match:
            # vector name using 'name[key]' syntax
            name, key = match.groups()
            try:
                return name, int(key)
            except ValueError:
                return name, key

        # Must be scalar name
        return name, None

    # combine_name() {{{2
    @classmethod
    def combine_name(cls, name, key=None):
        # Inverse of split_name().

        # convert underscores to dashes
        #name = name.replace('_', '-')

        if key is None:
            return name
        else:
            return '%s.%s' % (name, key)

    # get_value() {{{2
    @classmethod
    def get_value(cls, name=None):
        """Get Account Value

        Return value from the account given a user friendly identifier. User
        friendly identifiers include:
            name: scalar value
            name.key or name[key]:
                member of a dict or array
                dict if key is string, array if key is number
        """
        value = cls.get_field(*cls.split_name(name))
        if isinstance(value, Secret) or isinstance(value, Obscure):
            value = str(value)
        return value

    # write_summary() {{{2
    @classmethod
    def write_summary(cls):
        # present all account values that are not explicitly secret to the user

        def fmt_field(key, value='', level=0):
            if '\n' in value:
                value = indent(dedent(value), get_setting('indent')).strip('\n')
                sep = '\n'
            elif value:
                sep = ' '
            else:
                sep = ''
            key = str(key).upper().replace('_', ' ')
            leader = level*get_setting('indent')
            return indent(LabelColor(key + ':') + sep + value, leader)

        def reveal(name, key=None):
            return "<reveal with 'avendesora value %s %s'>" % (
                cls.get_name(), cls.combine_name(name, key)
            )

        def extract_collection(name, collection):
            lines = [fmt_field(key)]
            for k, v in items(collection):
                if hasattr(v, 'generate'):
                    # is a secret, get description if available
                    try:
                        v = '%s %s' % (v.get_key(), reveal(name, k))
                    except AttributeError:
                        v = reveal(name, k)
                lines.append(fmt_field(k, v, level=1))
            return lines

        # preload list with the names associated with this account
        names = [cls.get_name()]
        if hasattr(cls, 'aliases'):
            names += split(cls.aliases)
        lines = [fmt_field('names', ', '.join(names))]

        for key, value in cls.items():
            if key in TOOL_FIELDS:
                # is an Avendesora field
                pass
            elif is_collection(value):
                lines += extract_collection(key, value)
            elif hasattr(value, 'generate'):
                lines.append(fmt_field(key, reveal(key)))
            else:
                lines.append(fmt_field(key, value))
        output(*lines, sep='\n')

    # archive() {{{2
    @classmethod
    def archive(cls):
        # return all account fields along with their values as a dictionary

        def extract(value, name, key=None):
            if not is_collection(value):
                if hasattr(value, 'generate'):
                    value.generate(name, key, cls)
                    #value = 'Hidden(%s)' % Obscure.hide(str(value))
                return value
            try:
                return {k: extract(v, name, k) for k, v in value.items()}
            except AttributeError:
                # still need to work out how to output the question.
                return [extract(v, name, i) for i, v in enumerate(value)]

        return {k: extract(v, k) for k, v in cls.items() if k != 'master'}

    # open_browser() {{{2
    @classmethod
    def open_browser(cls, name, key=None):
        browser = cls.get_field('browser', default=None)
        if browser is None or is_str(browser):
            browser = StandardBrowser(name)

        # get the urls from the urls attribute
        if not key:
            key = getattr(cls, 'default_url', None)
        urls = getattr(cls, 'urls', [])
        if type(urls) != dict:
            if is_str(urls):
                urls = urls.split()
            urls = {None: urls}

        # get the urls from the url recognizers
        # currently urls from recognizers dominate over those from attributes
        discovery = getattr(cls, 'discovery', ())
        for each in values(discovery):
            urls.update(each.all_urls())

        # select the urls
        try:
            urls = urls[key]
        except TypeError:
            if key:
                raise Error(
                    'keys are not supported with urls on this account.',
                    culprit=self.get_name()
                )
        except KeyError:
            raise Error(
                'unknown key, choose from %s.' % conjoin(urls.keys()),
                culprit=key
            )
        url = next(split(urls))  # use the first url specified

        # open the url
        browser.run(url)


# StealthAccount class {{{1
class StealthAccount(Account):
    __NO_MASTER = True
        # prevents master password from being added to this base class

    @classmethod
    def get_seed(cls):
        # need to handle case where stdin/stdout is not available.
        # perhaps write generic password getter that supports both gui and tui.
        # Then have global option that indicates which should be used.
        # Separate name from seed. Only request seed when generating a password.
        import getpass
        try:
            name = getpass.getpass('account name: ')
        except EOFError:
            output()
            name = ''
        if not name:
            warn('null account name.')
        return name

    @classmethod
    def archive(cls):
        # do not archive stealth accounts
        pass

