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
        passphrase = account.get_value()
    except PasswordError as err:
        passphrase = err
    assert str(passphrase) == 'franc hypocrite newsflash dollop migraine amethyst'
    assert passphrase.render() == 'passcode: franc hypocrite newsflash dollop migraine amethyst'
    assert passphrase.render('{n} = {v}') == 'passcode = franc hypocrite newsflash dollop migraine amethyst'

def test_mybank_accounts_checking():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('mybank')
        checking = account.get_value('accounts.checking')
    except PasswordError as err:
        checking = err
    assert str(checking) == '12345678'

def test_mybank_accounts_checking2():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('mybank')
        checking = account.get_scalar('accounts', 'checking')
    except PasswordError as err:
        checking = str(err)
    assert str(checking) == '12345678'

def test_xkcd():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('xkcd', stealth_name='chaos')
        password = account.get_value()
    except PasswordError as err:
        password = err
    assert str(password) == 'tauten polymer rudder lively'

def test_alertscc():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('alertscc')
        password = account.get_value('password')
    except PasswordError as err:
        password = err
    assert str(password) == 'R7ibHyPjWtG2'

    try:
        password = account.get_value(('password',))
    except PasswordError as err:
        password = err
    assert str(password) == 'R7ibHyPjWtG2'

def test_alertscc_seed():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('alertscc', request_seed='chaos')
        password = account.get_value('password')
    except PasswordError as err:
        password = err
    assert str(password) == 'E3wx6hNqU2Zu'

def test_alertscc_question1():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('alertscc')
        answer = account.get_value(1)
    except PasswordError as err:
        answer = err
    assert str(answer) == 'tavern restate dogma'
    assert answer.render() == 'questions.1 (What street did you grow up on?): tavern restate dogma'
    assert answer.render('{d} {v}') == 'What street did you grow up on? tavern restate dogma'

def test_alertscc_question2():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('alertscc')
        answer = account.get_scalar('questions', 2)
    except PasswordError as err:
        answer = err
    assert str(answer) == 'vestige corny convector'

    try:
        answer = account.get_value('questions[2]')
    except PasswordError as err:
        answer = err
    assert str(answer) == 'vestige corny convector'
    assert answer.render() == 'questions.2 (What was your childhood nickname?): vestige corny convector'
    assert answer.render('{d} {v}') == 'What was your childhood nickname? vestige corny convector'

    try:
        answer = account.get_value(('questions', 2))
    except PasswordError as err:
        answer = err
    assert str(answer) == 'vestige corny convector'
    assert answer.render() == 'questions.2 (What was your childhood nickname?): vestige corny convector'
    assert answer.render('{d} {v}') == 'What was your childhood nickname? vestige corny convector'

    try:
        answer = account.get_value((2))
    except PasswordError as err:
        answer = err
    assert str(answer) == 'vestige corny convector'
    assert answer.render() == 'questions.2 (What was your childhood nickname?): vestige corny convector'
    assert answer.render('{d} {v}') == 'What was your childhood nickname? vestige corny convector'

def test_alertscc_questions():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('alertscc')
        expected = [
            'questions.0 (What city were you born in?): natty dipper kitty',
            'questions.1 (What street did you grow up on?): tavern restate dogma',
            'questions.2 (What was your childhood nickname?): vestige corny convector',
        ]
        for i, answer in account.get_values('questions'):
            assert expected[i] == answer.render()
    except PasswordError as err:
        assert str(err) == None

