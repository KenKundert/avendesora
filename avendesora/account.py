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
from .collection import Collection
from .config import get_setting
from .obscure import Obscure
from .preferences import TOOL_FIELDS
from .recognize import Recognizer
from .secrets import Secret
from inform import (
    Color, conjoin, cull, debug, Error, is_collection, is_str, log, output,
    warn, indent
)
from textwrap import dedent
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
import re
import sys


# Globals {{{1
VECTOR_PATTERN = re.compile(r'\A(\w+)\[(\w+)\]\Z')
LabelColor = Color(
    color=get_setting('label_color'),
    scheme=get_setting('color_scheme'),
    enable=Color.isTTY()
)

# AccountValue class {{{1
class AccountValue:
    """An Account Value

    Contains three attributes:
        value: the actual value
        is_secret: whether the value is secret or contains a secret
        label: a descriptive name for the value if the value of a  simple field is requested
    """
    def __init__(self, value, is_secret, label=None):
        self.value = value
        self.is_secret = is_secret
        self.label = label

    def __str__(self):
        return str(self.value)

    def render(self, sep=': '):
        if self.label is not None:
            return self.label + sep + str(self.value)
        return str(self.value)

    def __iter__(self):
        for each in [self.value, self.is_secret, self.label]:
            yield each

# Script class {{{1
class Script:
    """Script

    Takes a string that contains attributes. Those attributes are expanded
    before being output. For example, 'username: {username}, password:
    {passcode}' (this happens to be the default if no script is given. In this
    case, {username} and {passcode} are replaced by with the value of the
    corresponding account attribute. In addition to the account attributes,
    {tab} and {return} are replaced by a tab or carriage return character.
    """
    def __init__(self, script = 'username: {username}, password: {passcode}'):
        self.script = script

    def render(self, account):
        return str(account.get_value(self.script))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.script)

# Account class {{{1
class Account(object):
    __NO_MASTER = True
        # prevents master seed from being added to this base class

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

    # override_master() {{{2
    @classmethod
    def request_seed(cls):
        return getattr(cls, '_interactive_seed', False)


    # add_fileinfo() {{{2
    @classmethod
    def add_fileinfo(cls, master, fileinfo):
        if master and not hasattr(cls, '_%s__NO_MASTER' % cls.__name__):
            if not hasattr(cls, 'master'):
                cls.master = master
                cls._master_source = 'file'
            else:
                cls._master_source = 'account'
        cls._file_info = fileinfo

    # matches_exactly() {{{2
    @classmethod
    def matches_exactly(cls, account):
        if account == cls.get_name():
            return True
        try:
            if account in Collection(cls.aliases):
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
            for alias in Collection(cls.aliases):
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
                    for k, v in Collection(value).items():
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
        for recognizer in Collection(discovery):
            if isinstance(recognizer, Recognizer):
                script = recognizer.match(data, cls, verbose)
                name = getattr(recognizer, 'name', None)
                if script:
                    yield name, script
        if discovery:
            return

        # If no recognizers specified, just check the urls
        for url in Collection(cls.get_field('urls', default=[])):
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
    def initialize(cls, interactive_seed=False):
        cls._interactive_seed = interactive_seed
        log('initializing', cls.get_name())
        try:
            if cls.master.is_secure():
                if not cls._file_info.encrypted:
                    warn(
                        'high value master seed not contained in encrypted',
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
        "Get field Value given a field name and key"
        value = getattr(cls, name, None)
        if value is None:
            if name == 'NAME':
                return self.get_name()
            if default is False:
                raise Error(
                    'not found.',
                    culprit=(cls.get_name(), cls.combine_name(name, key))
                )
            return default

        if key is None:
            if is_collection(value):
                choices = {}
                for k, v in Collection(value).items():
                    try:
                        desc = v.get_key()
                    except AttributeError:
                        desc = None
                    if desc:
                        choices['   %s: %s' % (k, desc)] = k
                    else:
                        choices['   %s:' % k] = k
                raise Error(
                    'composite value found, need key. Choose from:',
                    *sorted(choices.keys()),
                    sep = '\n',
                    culprit = name,
                    is_collection = True,
                    collection = choices
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
        if isinstance(value, Script):
            value = value.render(cls)
        else:
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
    def get_value(cls, field=None):
        """Get Account Value

        Return value from the account given a user friendly identifier or
        script. User friendly identifiers include:
            None: value of default attribute
            name: scalar value
            name.key or name[key]:
                member of a dictionary or array
                key is string for dictionary, integer for array
        Scripts are simply strings with embedded attributes. Ex:
            'username: {username}, password: {passcode}'
        Returns a tuple: value, is_secret, label
        """

        # get default if field was not given
        if not field:
            name, key = cls.split_name(field)
            field = '.'.join(cull([name, key]))

        # determine whether field is actually a script
        is_script = is_str(field) and '{' in field and '}' in field

        # treat field as name rather than script if it there are no attributes
        if not is_script:
            name, key = cls.split_name(field)
            try:
                value = cls.get_field(name, key)
            except Error as err:
                err.terminate()
            is_secret = cls.is_secret(name, key)
            label = cls.combine_name(name, key)
            try:
                alt_name = value.get_key()
                if alt_name:
                    label += ' (%s)' % alt_name
            except AttributeError:
                pass
            if isinstance(value, Secret) or isinstance(value, Obscure):
                value = str(value)
            value =  dedent(value).strip() if is_str(value) else value
            return AccountValue(value, is_secret, label)

        # run the script
        script = field
        regex = re.compile(r'({[\w. ]+})')
        out = []
        is_secret = False
        for term in regex.split(script):
            if term and term[0] == '{' and term[-1] == '}':
                # we have found a command
                cmd = term[1:-1].lower()
                if cmd == 'tab':
                    out.append('\t')
                elif cmd == 'return':
                    out.append('\n')
                elif cmd.startswith('sleep '):
                    pass
                else:
                    name, key = cls.split_name(cmd)
                    try:
                        value = cls.get_field(name, key)
                        out.append(dedent(str(value)).strip())
                        if cls.is_secret(name, key):
                            is_secret = True
                    except Error as err:
                        err.terminate()
            else:
                out.append(term)
        return AccountValue(''.join(out), is_secret)

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
            key = str(key).replace('_', ' ')
            leader = level*get_setting('indent')
            return indent(LabelColor(key + ':') + sep + value, leader)

        def reveal(name, key=None):
            return "<reveal with 'avendesora value %s %s'>" % (
                cls.get_name(), cls.combine_name(name, key)
            )

        def extract_collection(name, collection):
            lines = [fmt_field(key)]
            for k, v in Collection(collection).items():
                if hasattr(v, 'generate'):
                    # is a secret, get description if available
                    try:
                        v = ' '.join(cull([v.get_key(), reveal(name, k)]))
                    except AttributeError:
                        v = reveal(name, k)
                lines.append(fmt_field(k, v, level=1))
            return lines

        # preload list with the names associated with this account
        names = [cls.get_name()]
        if hasattr(cls, 'aliases'):
            names += Collection(cls.aliases)
        lines = [fmt_field('names', ', '.join(names))]

        for key, value in cls.items():
            if key in TOOL_FIELDS:
                pass  # is an Avendesora field
            elif is_collection(value):
                lines += extract_collection(key, value)
            elif hasattr(value, 'generate'):
                lines.append(fmt_field(key, reveal(key)))
            elif hasattr(value, 'render'):
                lines.append(fmt_field(key, '<%s>' % value.script))
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
    def open_browser(cls, browser_name, key=None):
        if not browser_name:
            browser_name = cls.get_field('browser', default=None)
        browser = StandardBrowser(browser_name)

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
        for each in Collection(discovery):
            urls.update(each.all_urls())

        # select the urls
        try:
            urls = urls[key]
        except TypeError:
            if key:
                raise Error(
                    'keys are not supported with urls on this account.',
                    culprit=key
                )
        except KeyError:
            keys = cull(urls.keys())
            if keys:
                raise Error(
                    'unknown key, choose from %s.' % conjoin(keys),
                    culprit=key
                )
            else:
                raise Error(
                    'keys are not supported with urls on this account.',
                    culprit=key
                )
        url = list(Collection(urls))[0]  # use the first url specified

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

