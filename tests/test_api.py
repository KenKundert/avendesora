import pytest
import os

# set various environment variables so avendesora uses local gpg key and config
# directory rather than the users.
os.environ['HOME'] = 'home'

# change the current working directory to the test directory
cwd = os.getcwd()
if not cwd.endswith('/tests'):
    os.chdir('tests')

from avendesora import PasswordGenerator, PasswordError

def test_login():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('login')
        passphrase = account.get_value().value
    except PasswordError as err:
        passphrase = str(err)
    assert passphrase == 'franc hypocrite newsflash dollop migraine amethyst'

def test_mybank_accounts_checking():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('mybank')
        checking = account.get_value('accounts.checking').value
    except PasswordError as err:
        checking = str(err)
    assert checking == '12345678'

def test_mybank_accounts_checking2():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('mybank')
        checking = account.get_field('accounts', 'checking')
    except PasswordError as err:
        checking = str(err)
    assert str(checking) == '12345678'

def test_alertscc():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('alertscc')
        password = account.get_value('password').value
    except PasswordError as err:
        password = str(err)
    assert password == 'R7ibHyPjWtG2'

def test_alertscc_question1():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('alertscc')
        answer = account.get_value(1).value
    except PasswordError as err:
        answer = str(err)
    assert answer == 'tavern restate dogma'

def test_alertscc_question2():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('alertscc')
        answer = account.get_field('questions', 2)
    except PasswordError as err:
        answer = str(err)
    assert str(answer) == 'vestige corny convector'
