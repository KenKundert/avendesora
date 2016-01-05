from __future__ import print_function
from messenger import log
from .preferences import SEARCH_FIELDS

ken = "Ken's master password"

class Account(type):
    def __init__(self):
        raise NotImplementedError

    @classmethod
    def all_accounts(cls):
        for sub in cls.__subclasses__(cls):
            yield sub
            for sub in sub.all_accounts():
                yield sub

    @classmethod
    def get_name(cls):
        try:
            return cls.name
        except AttributeError:
            # consider converting lower to upper case transitions in __name__ to 
            # dashes.
            return cls.__name__.lower()

    @classmethod
    def matches_exactly(cls, account):
        if account == cls.get_name():
            return True
        try:
            if account in cls.aliases:
                return True
        except AttributeError:
            pass
        return False

    @classmethod
    def id_contains(cls, target):
        if target in cls.get_name():
            return True
        try:
            for alias in cls.aliases:
                if target in alias:
                    return True
        except AttributeError:
            pass
        return False

    @classmethod
    def account_contains(cls, target):
        if cls.id_contains(target):
            return True
        for field in SEARCH_FIELDS:
            try:
                if target in cls.__dict__[field]:
                    return True
            except KeyError:
                pass
        return False

    @classmethod
    def initialize(cls):
        log('initializing', cls.get_name())
        for key, value in cls.__dict__.items():
            if not key.startswith('__'):
                log('    initializing attribute', key)
                try:
                    value._initiate(key, cls)
                except AttributeError:
                    try:
                        for i, each in enumerate(value):
                            name = 'ken[%s]' % i
                            each._initiate(name, cls)
                    except AttributeError:
                        pass

    @classmethod
    def values(cls):
        for key in sorted(cls.__dict__):
            if not key.startswith('__'):
                yield key, cls.__dict__[key]

    @classmethod
    def get_value(cls, name):
        return cls.__dict__.get(name)
