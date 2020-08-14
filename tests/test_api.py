from textwrap import dedent
import pytest
import os
from inform import Inform

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

def test_mybank_accounts_checking3():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('mybank')
        checking = account.get_scalar('checking')
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

def test_xkcd2():
    try:
        pw = PasswordGenerator()
        password = pw.get_value('xkcd', stealth_name='chaos')
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

def test_alertscc2():
    try:
        pw = PasswordGenerator()
        password = pw.get_value('alertscc:password')
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

def test_mybank_accounts():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('mybank')
        expected = dict(
            checking='12345678',
            savings='23456789',
            creditcard='34567890'
        )
        for k, v in account.get_values('accounts'):
            assert str(v) == expected[k]
    except PasswordError as err:
        assert str(err) == None

def test_unknown_account():
    try:
        pw = PasswordGenerator()
        account = pw.get_account('alertsdd')
    except PasswordError as err:
        assert str(err) == 'alertsdd: account not found, did you mean:\n    alertscc (scc)?'

def test_search_accounts():
    try:
        pw = PasswordGenerator()
        matches = set()
        for acct in pw.search_accounts('my'):
            matches.add(acct.get_name())
        assert ' '.join(matches) == 'mybank'
    except PasswordError as err:
        assert str(err) == None

def test_find_accounts():
    try:
        pw = PasswordGenerator()
        matches = set()
        for acct in pw.find_accounts('my'):
            matches.add(acct.get_name())
        assert ' '.join(matches) == 'mybank'
    except PasswordError as err:
        assert str(err) == None

def test_recognize1():
    try:
        pw = PasswordGenerator()
        script = pw.discover_account(title='easy peasy')
        assert script.account.get_name() == 'mybank'
        assert repr(script) == "Script('lemon squeezy')"
    except PasswordError as err:
        assert str(err) == None

def test_recognize2():
    try:
        pw = PasswordGenerator()
        script = pw.discover_account(title='Margaritaville - https://www.margaritaville.com/home - Firefox')
        assert script.account.get_name() == 'margaritaville'
        assert repr(script) == "Script('{passcode}{return}')"
    except PasswordError as err:
        assert str(err) == None

def test_summary(capsys):
    try:
        with Inform(prog_name=False):
            pw = PasswordGenerator()
            account = pw.get_account('mybank')
            stdout, stderr = capsys.readouterr()
            assert stdout == ''
            assert stderr == ''
            account.write_summary(sort=True)
            stdout, stderr = capsys.readouterr()
            assert stderr == ''
            assert stdout == dedent('''
                names: mybank, mb
                accounts:
                    checking: reveal with: avendesora value mybank accounts.checking
                    savings: reveal with: avendesora value mybank accounts.savings
                    creditcard: reveal with: avendesora value mybank accounts.creditcard
                birthdate: 1981-10-01
                checking: {accounts.checking}
                comment:
                    This is a multiline comment.
                    It spans more than one line.
                customer service: 1-866-229-6633
                email: pizzaman@pizza.com
                passcode: reveal with: avendesora value mybank passcode
                pin: reveal with: avendesora value mybank pin
                questions:
                    0: What city were you born in?, reveal with: avendesora value mybank questions.0
                    1: What street did you grow up on?, reveal with: avendesora value mybank questions.1
                    2: What was your childhood nickname?, reveal with: avendesora value mybank questions.2
                urls: https://mb.com
                username: pizzaman
                verbal: reveal with: avendesora value mybank verbal
            ''').lstrip()
    except PasswordError as err:
        assert str(err) == None

def test_composite(capsys):
    with Inform(prog_name=False):
        pw = PasswordGenerator()
        account = pw.get_account('mybank')
        accounts = account.get_composite('accounts')
        assert accounts == dict(
            checking='12345678',
            savings='23456789',
            creditcard='34567890'
        )
        questions = account.get_composite('questions')
        assert questions == [
            'scallywag bedbug groupie',
            'assay centrist fanatic',
            'shunt remnant burrow'
        ]
        pin = account.get_composite('pin')
        assert pin == '9982'
        name = account.get_composite('NAME')
        assert name == 'mybank'
        nada = account.get_composite('nada')
        assert nada == None

def test_archive(capsys):
    from avendesora import Hidden, OTP, Question, RecognizeTitle, Script
    from inform import render
    with Inform(prog_name=False):
        pw = PasswordGenerator()
        account = pw.get_account('mybank')
        archive = account.archive()
        expected = dict(
            accounts = dict(
                checking = Hidden('MTIzNDU2Nzg='),
                creditcard = Hidden('MzQ1Njc4OTA='),
                savings = Hidden('MjM0NTY3ODk=')
            ),
            aliases = 'mb'.split(),
            birthdate = Hidden('MTk4MS0xMC0wMQ==', is_secret=False),
            checking = Script('{accounts.checking}'),
            comment = dedent('''
                This is a multiline comment.
                It spans more than one line.
            '''),
            customer_service = '1-866-229-6633',
            discovery = RecognizeTitle('easy peasy', script='lemon squeezy'),
            email = 'pizzaman@pizza.com',
            passcode = Hidden('b1UkJHcwVU1YZTc0'),
            pin = Hidden('OTk4Mg=='),
            questions = [
                Question(
                    'What city were you born in?',
                    answer=Hidden('c2NhbGx5d2FnIGJlZGJ1ZyBncm91cGll')
                ),
                Question(
                    'What street did you grow up on?',
                    answer=Hidden('YXNzYXkgY2VudHJpc3QgZmFuYXRpYw==')
                ),
                Question(
                    'What was your childhood nickname?',
                    answer=Hidden('c2h1bnQgcmVtbmFudCBidXJyb3c=')
                )
            ],
            urls = 'https://mb.com',
            username = 'pizzaman',
            verbal = Hidden('Zml6emxlIGxlb3BhcmQ=')
        )
        #with open('expected', 'w') as f:
        #    f.write(render(expected, sort=True))
        #with open('result', 'w') as f:
        #    f.write(render(archive, sort=True))
        assert render(archive, sort=True) == render(expected, sort=True)


if __name__ == '__main__':
    # As a debugging aid allow the tests to be run on their own, outside pytest.
    # This makes it easier to see and interpret and textual output.

    defined = dict(globals())
    for k, v in defined.items():
        if callable(v) and k.startswith('test_'):
            print()
            print('Calling:', k)
            print((len(k)+9)*'=')
            v()
