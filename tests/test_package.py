import pytest
import os

# set various environment variables so avendesora uses local gpg key and config
# directory rather than the users.

os.environ['HOME'] = 'home'

from avendesora import PasswordGenerator, Error

def test_login():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('login')
        passphrase = account.get_value()
    except Error as err:
        passphrase = str(err)
    assert passphrase == 'enthrall sunflower screening order shard rejoin'

def test_mybank_accounts_checking():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('mybank')
        checking = account.get_value('accounts.checking')
    except Error as err:
        checking = str(err)
    assert checking == '12345678'

def test_mybank_accounts_checking2():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('mybank')
        checking = account.get_field('accounts', 'checking')
    except Error as err:
        checking = str(err)
    assert str(checking) == '12345678'

def test_alertscc():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('alertscc')
        password = account.get_value()
        password2 = account.get_value()
    except Error as err:
        password = str(err)
        password2 = str(err)
    assert password == 'KLwuU8itfect'
    assert password2 == 'KLwuU8itfect'

def test_alertscc_question1():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('alertscc')
        answer = account.get_value(1)
    except Error as err:
        answer = str(err)
    assert answer == 'placate rocky barge'

def test_alertscc_question2():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('alertscc')
        answer = account.get_field('questions', 2)
    except Error as err:
        answer = str(err)
    assert str(answer) == 'jigsaw tilde century'
