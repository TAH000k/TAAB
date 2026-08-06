"""
Security utilities for password handling.
Provides functions for securely hashing passwords and verifying 
plain-text passwords against stored hashes using pwdlib.
"""

from pwdlib import PasswordHash

# Initialize the password hashing context with recommended default algorithms
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using the recommended hashing algorithm.

    Args:
        password (str): The plain-text password to hash.

    Returns:
        str: The resulting secure password hash.
    """
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifies a plain-text password against an existing password hash.

    Args:
        password (str): The plain-text password to verify.
        password_hash (str): The stored password hash to compare against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return password_hasher.verify(password, password_hash)
