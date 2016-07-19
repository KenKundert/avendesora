import pytest
import subprocess
import os

# set various environment variables so avendesora uses local gpg key and config
# directory rather than the users.

os.environ['HOME'] = 'home'

def test_mybank():
    result = subprocess.check_output('avendesora --stdout mybank'.split())
    assert result == b'NNPx2dHiR7mo\n'

def test_mb():
    result = subprocess.check_output('avendesora --stdout mb'.split())
    assert result == b'NNPx2dHiR7mo\n'

def test_mb_checking():
    result = subprocess.check_output('avendesora --stdout mb accounts.checking'.split())
    assert result == b'12345678\n'

def test_mb_savings():
    result = subprocess.check_output('avendesora --stdout mb accounts[savings]'.split())
    assert result == b'23456789\n'

def test_alertscc():
    result = subprocess.check_output('avendesora --stdout alertscc'.split())
    assert result == b'UnmvA52NYMha\n'

def test_scc():
    result = subprocess.check_output('avendesora --stdout scc'.split())
    assert result == b'UnmvA52NYMha\n'

def test_scc_account():
    result = subprocess.check_output('avendesora --stdout scc account'.split())
    assert result == b'123456-7890\n'

def test_scc_birthdate():
    result = subprocess.check_output('avendesora --stdout scc birthdate'.split())
    assert result == b'1969-12-28\n'

def test_scc_email():
    result = subprocess.check_output('avendesora --stdout scc email'.split())
    assert result == b'pizzaman@pizza.com\n'

def test_scc_q0():
    result = subprocess.check_output('avendesora --stdout scc 0'.split())
    assert result == b'attendant oppress dimple\n'

def test_scc_q1():
    result = subprocess.check_output('avendesora --stdout scc questions.1'.split())
    assert result == b'student camera bleach\n'

def test_scc_q2():
    result = subprocess.check_output('avendesora --stdout scc questions[2]'.split())
    assert result == b'workforce simulcast smelt\n'

def test_login():
    result = subprocess.check_output('avendesora --stdout login'.split())
    assert result == b'racket genetic outbreak earlobe waterway fatality\n'
