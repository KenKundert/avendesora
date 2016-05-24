import pytest
import subprocess
import os

# set various environment variables so avendesora uses local gpg key and config
# directory rather than the users.

os.environ['HOME'] = 'home'

def test_mybank():
    result = subprocess.check_output('avendesora -g 21CEB56F mybank'.split())
    assert result == b'None = ovhVFZnMD2d6\n'

def test_mb():
    result = subprocess.check_output('avendesora -g 21CEB56F mb'.split())
    assert result == b'None = ovhVFZnMD2d6\n'

def test_alertscc():
    result = subprocess.check_output('avendesora -g 21CEB56F alertscc'.split())
    assert result == b'None = YxHP5EBK9gqK\n'

def test_scc():
    result = subprocess.check_output('avendesora -g 21CEB56F scc'.split())
    assert result == b'None = YxHP5EBK9gqK\n'
