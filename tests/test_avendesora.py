import pytest
from inform import os_error
from textwrap import dedent
import subprocess
import os

# set various environment variables so avendesora uses local gpg key and config
# directory rather than the users.

os.environ['HOME'] = 'home'

# test_mybank() {{{1
def test_mybank():
    try:
        result = subprocess.check_output('avendesora value --stdout mybank'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'jFi$TH66w*Fg\n'

# test_mb() {{{1
def test_mb():
    try:
        result = subprocess.check_output('avendesora value --stdout mb'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'jFi$TH66w*Fg\n'

# test_mb_checking() {{{1
def test_mb_checking():
    try:
        result = subprocess.check_output('avendesora value --stdout mb accounts.checking'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'12345678\n'

# test_mb_savings() {{{1
def test_mb_savings():
    try:
        result = subprocess.check_output('avendesora value --stdout mb accounts[savings]'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'23456789\n'

# test_alertscc() {{{1
def test_alertscc():
    try:
        result = subprocess.check_output('avendesora value --stdout alertscc'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'KLwuU8itfect\n'

# test_scc() {{{1
def test_scc():
    try:
        result = subprocess.check_output('avendesora value --stdout scc'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'KLwuU8itfect\n'

# test_scc_account() {{{1
def test_scc_account():
    try:
        result = subprocess.check_output('avendesora value --stdout scc account'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'123456-7890\n'

# test_scc_birthdate() {{{1
def test_scc_birthdate():
    try:
        result = subprocess.check_output('avendesora value --stdout scc birthdate'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'1963-04-10\n'

# test_scc_email() {{{1
def test_scc_email():
    try:
        result = subprocess.check_output('avendesora value --stdout scc email'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'pizzaman@pizza.com\n'

# test_scc_q0() {{{1
def test_scc_q0():
    try:
        result = subprocess.check_output('avendesora value --stdout scc 0'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'gyroscope ossify slink\n'

# test_scc_q1() {{{1
def test_scc_q1():
    try:
        result = subprocess.check_output('avendesora value --stdout scc questions.1'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'placate rocky barge\n'

# test_scc_q2() {{{1
def test_scc_q2():
    try:
        result = subprocess.check_output('avendesora value --stdout scc questions[2]'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'jigsaw tilde century\n'

# test_login() {{{1
def test_login():
    try:
        result = subprocess.check_output('avendesora value --stdout login'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'enthrall sunflower screening order shard rejoin\n'

# test_summary() {{{1
def test_summary():
    try:
        result = subprocess.check_output('avendesora values mb'.split())
    except OSError as err:
        result = os_error(err)
    expected = dedent("""\
        NAMES: mybank, mb
        ACCOUNTS:
            CHECKING: <reveal with 'avendesora value mybank accounts.checking'>
            CREDITCARD: <reveal with 'avendesora value mybank accounts.creditcard'>
            SAVINGS: <reveal with 'avendesora value mybank accounts.savings'>
        CUSTOMER SERVICE: 1-866-229-6633
        EMAIL: pizzaman@pizza.com
        PASSCODE: <reveal with 'avendesora value mybank passcode'>
        PIN: <reveal with 'avendesora value mybank pin'>
        QUESTIONS:
            0: What city were you born in? <reveal with 'avendesora value mybank questions.0'>
            1: What street did you grow up on? <reveal with 'avendesora value mybank questions.1'>
            2: What was your childhood nickname? <reveal with 'avendesora value mybank questions.2'>
        URLS: https://mb.com
        USERNAME: pizzaman
        VERBAL: <reveal with 'avendesora value mybank verbal'>
    """)
    assert result == bytes(expected, encoding='ascii')

# test_find() {{{1
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

# test_search() {{{1
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

# test_reveal() {{{1
def test_reveal():
    try:
        result = subprocess.check_output('avendesora reveal MTIzNDU2Nzg='.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'12345678\n'

# test_conceal() {{{1
def test_conceal():
    try:
        result = subprocess.check_output('avendesora conceal 12345678'.split())
    except OSError as err:
        result = os_error(err)
    assert result == b'MTIzNDU2Nzg=\n'
