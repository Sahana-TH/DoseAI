# filepath: tests/test_lookup.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.medicine_lookup import get_medicine_info

def test_paracetamol_lookup():
    """Test looking up Paracetamol."""
    result = get_medicine_info('Paracetamol')
    assert result is not None
    assert result['name'] == 'Paracetamol'
    assert 'pain relief' in result['uses'].lower()

def test_case_insensitive():
    """Test that lookup is case-insensitive."""
    result = get_medicine_info('paracetamol')
    assert result is not None

def test_not_found():
    """Test medicine not found."""
    result = get_medicine_info('FakeMedicine123')
    assert result is None

if __name__ == '__main__':
    test_paracetamol_lookup()
    test_case_insensitive()
    test_not_found()
    print("All tests passed!")