import pytest
import subprocess
import os

# set various environment variables so avendesora uses local gpg key and config
# directory rather than the users.

os.environ['HOME'] = 'home'

def test_mybank():
    result = subprocess.check_output('avendesora -g 21CEB56F --stdout mybank'.split())
    assert result == b'ovhVFZnMD2d6\n'

def test_mb():
    result = subprocess.check_output('avendesora -g 21CEB56F --stdout mb'.split())
    assert result == b'ovhVFZnMD2d6\n'

def test_mb_checking():
    result = subprocess.check_output('avendesora -g 21CEB56F --stdout mb accounts.checking'.split())
    assert result == b'12345678\n'

def test_mb_savings():
    result = subprocess.check_output('avendesora -g 21CEB56F --stdout mb accounts[savings]'.split())
    assert result == b'23456789\n'

def test_alertscc():
    result = subprocess.check_output('avendesora -g 21CEB56F --stdout alertscc'.split())
    assert result == b'YxHP5EBK9gqK\n'

def test_scc():
    result = subprocess.check_output('avendesora -g 21CEB56F --stdout scc'.split())
    assert result == b'YxHP5EBK9gqK\n'

def test_scc_account():
    result = subprocess.check_output('avendesora -g 21CEB56F --stdout scc account'.split())
    assert result == b'123456-7890\n'

def test_scc_birthdate():
    result = subprocess.check_output('avendesora -g 21CEB56F --stdout scc birthdate'.split())
    assert result == b'1979-05-02\n'

def test_scc_email():
    result = subprocess.check_output('avendesora -g 21CEB56F --stdout scc email'.split())
    assert result == b'pizzaman@pizza.com\n'

def test_scc_q0():
    result = subprocess.check_output('avendesora -g 21CEB56F --stdout scc 0'.split())
    assert result == b'attendant oppress dimple\n'

def test_scc_q1():
    result = subprocess.check_output('avendesora -g 21CEB56F --stdout scc questions.1'.split())
    assert result == b'student camera bleach\n'

def test_scc_q2():
    result = subprocess.check_output('avendesora -g 21CEB56F --stdout scc questions[2]'.split())
    assert result == b'workforce simulcast smelt\n'

def test_login():
    result = subprocess.check_output('avendesora -g 21CEB56F --stdout login'.split())
    assert result == b'widower governess undergo porthole smoothie worthy\n'
