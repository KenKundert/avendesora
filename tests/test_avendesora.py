import pytest
from inform import os_error
from textwrap import dedent
import subprocess
import os
import pexpect
import pyotp

# set various environment variables so avendesora uses local gpg key and config
# directory rather than the users.
os.environ['HOME'] = 'home'

# change the current working directory to the test directory
cwd = os.getcwd()
if not cwd.endswith('/tests'):
    os.chdir('tests')

# Run avendesora
# Explicitly calling the coverage analysis does not seem to be needed. Adding it
# does not change the coverage numbers.
def run(args):
    #args = args.split()
    #args[0] = './pw'
    #print(*(['coverage', 'run'] + args))
    #return subprocess.check_output(['coverage', 'run'] + args)
    return subprocess.check_output(args.split())

# test_mybank() {{{1
def test_mybank():
    try:
        result = run('avendesora value --stdout mybank')
    except OSError as err:
        result = os_error(err)
    assert result == b'oU$$w0UMXe74\n'

# test_mb() {{{1
def test_mb():
    try:
        result = run('avendesora value --stdout mb')
    except OSError as err:
        result = os_error(err)
    assert result == b'oU$$w0UMXe74\n'

# test_mb_checking() {{{1
def test_mb_checking():
    try:
        result = run('avendesora value --stdout mb accounts.checking')
    except OSError as err:
        result = os_error(err)
    assert result == b'12345678\n'

# test_mb_savings() {{{1
def test_mb_savings():
    try:
        result = run('avendesora value --stdout mb accounts[savings]')
    except OSError as err:
        result = os_error(err)
    assert result == b'23456789\n'

# test_mb_browse() {{{1
def test_mb_browse():
    try:
        result = run('avendesora browse --list  mb')
    except OSError as err:
        result = os_error(err)
    assert result == b'                        : https://mb.com [default]\n'

# test_alertscc() {{{1
def test_alertscc():
    try:
        result = run('avendesora value --stdout alertscc')
    except OSError as err:
        result = os_error(err)
    assert result == b'email is pizzaman@pizza.com, password is R7ibHyPjWtG2\n'

# test_alertscc_discovery() {{{1
def test_alertscc_discovery():
    try:
        result = run('avendesora value --title https://alertscc.bbcportal.com --stdout alertscc')
    except OSError as err:
        result = os_error(err)
    assert result == b'email is pizzaman@pizza.com, password is R7ibHyPjWtG2\n'

# test_alertscc_script() {{{1
def test_alertscc_script():
    try:
        result = run('avendesora value --stdout alertscc {email}#{password}')
    except OSError as err:
        result = os_error(err)
    assert result == b'pizzaman@pizza.com#R7ibHyPjWtG2\n'

# test_alertscc_browse() {{{1
def test_alertscc_browse():
    try:
        result = run('avendesora browse --list alertscc')
    except OSError as err:
        result = os_error(err)
    assert sorted(result) == sorted(
        b'              validation: https://alertscc.bbcportal.com/Validation\n'
        b'                   login: https://alertscc.bbcportal.com\n'
    )

# test_scc() {{{1
def test_scc():
    try:
        result = run('avendesora value --stdout scc')
    except OSError as err:
        result = os_error(err)
    assert result == b'email is pizzaman@pizza.com, password is R7ibHyPjWtG2\n'

# test_scc_account() {{{1
def test_scc_account():
    try:
        result = run('avendesora value --stdout scc account')
    except OSError as err:
        result = os_error(err)
    assert result == b'123456-7890\n'

# test_scc_birthdate() {{{1
def test_scc_birthdate():
    try:
        result = run('avendesora value --stdout scc birthdate')
    except OSError as err:
        result = os_error(err)
    assert result == b'1986-10-20\n'

# test_scc_email() {{{1
def test_scc_email():
    try:
        result = run('avendesora value --stdout scc email')
    except OSError as err:
        result = os_error(err)
    assert result == b'pizzaman@pizza.com\n'

# test_scc_q0() {{{1
def test_scc_q0():
    try:
        result = run('avendesora value --stdout scc 0')
    except OSError as err:
        result = os_error(err)
    assert result == b'natty dipper kitty\n'

# test_scc_q1() {{{1
def test_scc_q1():
    try:
        result = run('avendesora value --stdout scc questions.1')
    except OSError as err:
        result = os_error(err)
    assert result == b'tavern restate dogma\n'

# test_scc_q2() {{{1
def test_scc_q2():
    try:
        result = run('avendesora value --stdout scc questions[2]')
    except OSError as err:
        result = os_error(err)
    assert result == b'vestige corny convector\n'

# test_scc_browse() {{{1
def test_scc_browse():
    try:
        result = run('avendesora browse --list scc')
    except OSError as err:
        result = os_error(err)
    assert sorted(result) == sorted(
        b'              validation: https://alertscc.bbcportal.com/Validation\n'
        b'                   login: https://alertscc.bbcportal.com\n'
    )

# test_login() {{{1
def test_login():
    try:
        result = run('avendesora value --stdout login')
    except OSError as err:
        result = os_error(err)
    assert result == b'franc hypocrite newsflash dollop migraine amethyst\n'

# test_summary() {{{1
def test_summary():
    try:
        result = run('avendesora values -s mb')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""\
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
    """)
    assert result.decode('utf-8') == expected

# test_find() {{{1
def test_find():
    try:
        result = run('avendesora find bank')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""\
        bank:
            mybank (mb)
    """)
    assert result.decode('utf-8') == expected

# test_search() {{{1
def test_search():
    try:
        result = run('avendesora search pizza')
    except OSError as err:
        result = os_error(err)
    expected = dedent("""\
        pizza:
            alertscc (scc)
            margaritaville
            mybank (mb)
    """)
    assert result.decode('utf-8') == expected

# test_reveal() {{{1
def test_reveal():
    try:
        result = run('avendesora reveal Hidden("MTIzNDU2Nzg=")')
    except OSError as err:
        result = os_error(err)
    assert result == b'12345678\n'

# test_conceal() {{{1
def test_conceal():
    try:
        result = run('avendesora conceal 12345678')
    except OSError as err:
        result = os_error(err)
    assert result == "Hidden('MTIzNDU2Nzg=')\n".encode('ascii')

# test_stealth() {{{1
def test_stealth():
    try:
        avendesora = pexpect.spawn('avendesora', 'value -s xkcd'.split())
        avendesora.expect('account name: ', timeout=4)
        avendesora.sendline('an-account-name')
        avendesora.expect(pexpect.EOF)
        avendesora.close()
        result = avendesora.before.decode('utf-8')
    except (pexpect.EOF, pexpect.TIMEOUT):
        result = avendesora.before.decode('utf8')
    except OSError as err:
        result = os_error(err)
    assert result.strip() == 'underdog crossword apron whinny'

# test_alertscc_seed() {{{1
def test_alertscc_seed():
    try:
        avendesora = pexpect.spawn('avendesora', 'value -S -s alertscc password'.split())
        avendesora.expect('seed for alertscc: ', timeout=4)
        avendesora.sendline('frozen-chaos')
        avendesora.expect(pexpect.EOF)
        avendesora.close()
        result = avendesora.before.decode('utf-8')
    except (pexpect.EOF, pexpect.TIMEOUT):
        result = avendesora.before.decode('utf8')
    except OSError as err:
        result = os_error(err)
    assert result.strip() == 'tRT7vXLeZrbz'
# test_mybank_otp() {{{1
#def test_mybank_otp():
#    otp = pyotp.TOTP('JBSWY3DPEHPK3PXP')
#    try:
#        result = run('avendesora value --stdout mybank otp')
#    except OSError as err:
#        result = os_error(err)
#    assert result.decode('ascii').strip() == otp.now()
