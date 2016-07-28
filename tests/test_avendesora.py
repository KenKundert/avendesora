import pytest
from inform import os_error
from textwrap import dedent
import subprocess
import os

# set various environment variables so avendesora uses local gpg key and config
# directory rather than the users.

os.environ['HOME'] = 'home'

def test_mybank():
    try:
        result = subprocess.check_output('avendesora show --stdout mybank'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'&5U9eZ+iT84T\n'

def test_mb():
    try:
        result = subprocess.check_output('avendesora show --stdout mb'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'&5U9eZ+iT84T\n'

def test_mb_checking():
    try:
        result = subprocess.check_output('avendesora show --stdout mb accounts.checking'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'12345678\n'

def test_mb_savings():
    try:
        result = subprocess.check_output('avendesora show --stdout mb accounts[savings]'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'23456789\n'

def test_alertscc():
    try:
        result = subprocess.check_output('avendesora show --stdout alertscc'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'qfUfLViukFcJ\n'

def test_scc():
    try:
        result = subprocess.check_output('avendesora show --stdout scc'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'qfUfLViukFcJ\n'

def test_scc_account():
    try:
        result = subprocess.check_output('avendesora show --stdout scc account'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'123456-7890\n'

def test_scc_birthdate():
    try:
        result = subprocess.check_output('avendesora show --stdout scc birthdate'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'1978-10-18\n'

def test_scc_email():
    try:
        result = subprocess.check_output('avendesora show --stdout scc email'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'pizzaman@pizza.com\n'

def test_scc_q0():
    try:
        result = subprocess.check_output('avendesora show --stdout scc 0'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'sniff flashy putsch\n'

def test_scc_q1():
    try:
        result = subprocess.check_output('avendesora show --stdout scc questions.1'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'clipping knight guest\n'

def test_scc_q2():
    try:
        result = subprocess.check_output('avendesora show --stdout scc questions[2]'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'mistrust tumor bonfire\n'

def test_login():
    try:
        result = subprocess.check_output('avendesora show --stdout login'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'archangel fiesta ripen tracksuit autobahn integer\n'

def test_show_all():
    try:
        result = subprocess.check_output('avendesora showall mb'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""\
        NAMES: mybank, mb
        ACCOUNTS:
            CHECKING: <reveal with 'avendesora mybank accounts.checking'>
            CREDITCARD: <reveal with 'avendesora mybank accounts.creditcard'>
            SAVINGS: <reveal with 'avendesora mybank accounts.savings'>
        CUSTOMER SERVICE: 1-866-229-6633
        EMAIL: pizzaman@pizza.com
        PASSCODE: <reveal with 'avendesora mybank passcode'>
        PIN: <reveal with 'avendesora mybank pin'>
        QUESTIONS:
            0: What city were you born in? <reveal with 'avendesora mybank questions.0'>
            1: What street did you grow up on? <reveal with 'avendesora mybank questions.1'>
            2: What was your childhood nickname? <reveal with 'avendesora mybank questions.2'>
        URL: https://mb.com
        USERNAME: pizzaman
        VERBAL: <reveal with 'avendesora mybank verbal'>
    """)
    assert result == bytes(expected, encoding='ascii')

def test_find():
    try:
        result = subprocess.check_output('avendesora find bank'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""\
        bank:
            mybank (mb)
    """)
    assert result == bytes(expected, encoding='ascii')

def test_search():
    try:
        result = subprocess.check_output('avendesora search pizza'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""\
        pizza:
            alertscc (scc)
            mybank (mb)
    """)
    assert result == bytes(expected, encoding='ascii')

def test_reveal():
    try:
        result = subprocess.check_output('avendesora reveal MTIzNDU2Nzg='.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'12345678\n'

def test_conceal():
    try:
        result = subprocess.check_output('avendesora conceal 12345678'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'MTIzNDU2Nzg=\n'
