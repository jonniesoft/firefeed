#!/usr/bin/env python3
"""
Test script for password validation
"""

import sys

sys.path.append("/root/firefeed")

from api.models import PasswordResetConfirm, UserCreate


def test_password_validation():
    """Test password validation rules"""

    # Test 1: Valid password
    try:
        _user = UserCreate(email="test@example.com", password="MySecure123!", language="en")
        print("✅ Valid password accepted")
    except Exception as e:
        print(f"❌ Valid password rejected: {e}")

    # Test 2: Too short
    try:
        _user = UserCreate(email="test@example.com", password="Short1!", language="en")
        print("❌ Short password accepted (should be rejected)")
    except Exception as e:
        print(f"✅ Short password correctly rejected: {e}")

    # Test 3: No uppercase
    try:
        _user = UserCreate(email="test@example.com", password="nouppercase123!", language="en")
        print("❌ Password without uppercase accepted (should be rejected)")
    except Exception as e:
        print(f"✅ Password without uppercase correctly rejected: {e}")

    # Test 4: No digit
    try:
        _user = UserCreate(email="test@example.com", password="NoDigitsHere!", language="en")
        print("❌ Password without digits accepted (should be rejected)")
    except Exception as e:
        print(f"✅ Password without digits correctly rejected: {e}")

    # Test 5: No special character
    try:
        _user = UserCreate(email="test@example.com", password="NoSpecialChars123", language="en")
        print("❌ Password without special chars accepted (should be rejected)")
    except Exception as e:
        print(f"✅ Password without special chars correctly rejected: {e}")

    # Test 6: Common password
    try:
        _user = UserCreate(email="test@example.com", password="Password123!", language="en")
        print("❌ Common password accepted (should be rejected)")
    except Exception as e:
        print(f"✅ Common password correctly rejected: {e}")

    # Test 7: PasswordResetConfirm validation
    try:
        _reset = PasswordResetConfirm(token="abc123", new_password="NewSecure123!")
        print("✅ Valid reset password accepted")
    except Exception as e:
        print(f"❌ Valid reset password rejected: {e}")


if __name__ == "__main__":
    print("Testing password validation...")
    test_password_validation()
    print("\nAll tests completed!")
