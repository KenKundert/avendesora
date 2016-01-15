import pytest
import subprocess

def test_mybank():
    result = subprocess.check_output(['avendesora', 'mybank'])
    assert result == b'None = ovhVFZnMD2d6\n'

def test_mb():
    result = subprocess.check_output(['avendesora', 'mb'])
    assert result == b'None = ovhVFZnMD2d6\n'

def test_alertscc():
    result = subprocess.check_output(['avendesora', 'alertscc'])
    assert result == b'None = YxHP5EBK9gqK\n'

def test_scc():
    result = subprocess.check_output(['avendesora', 'scc'])
    assert result == b'None = YxHP5EBK9gqK\n'

