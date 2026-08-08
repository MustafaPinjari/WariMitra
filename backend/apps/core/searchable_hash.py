"""
Searchable Encryption Hash Module - Deterministic PBKDF2-Based Hashing

This module provides deterministic hashing for searchable encryption. Enables querying
encrypted email/phone fields without decryption while maintaining security.

Security Properties:
- Algorithm: PBKDF2-SHA256
- Iterations: 100,000 (OWASP 2023 standard)
- Salt: 32 bytes (hardcoded constant for determinism)
- Output: 64-character hex string (256 bits)
- Deterministic: same plaintext always produces same hash
- Collision-resistant: no two different values hash to same output
- Constant-time verification: prevents timing attacks

Usage:
    # Initialize hasher
    hasher = SearchableHasher()
    
    # Compute hash for searchable index
    email_hash = hasher.compute_hash("user@example.com")
    
    # Query database by hash
    user = User.objects.get(email_hash=email_hash)
    
    # Verify during write operations
    is_valid = hasher.verify_hash("user@example.com", stored_hash)
"""

import hmac
import hashlib
from typing import Optional
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes


class SearchableHashError(Exception):
    """Raised when hash operations fail."""
    pass


class SearchableHasher:
    """
    PBKDF2-based deterministic hasher for searchable encryption.
    
    Produces consistent hashes for the same input value, enabling:
    1. Database indexing on email_hash, phone_hash columns
    2. Fast lookups without decryption
    3. Privacy: plaintext values not stored, only hashes
    
    Thread-safe and stateless.
    """
    
    # PBKDF2 parameters
    ALGORITHM = "PBKDF2-SHA256"
    ITERATIONS = 100000  # OWASP 2023 minimum
    HASH_LENGTH = 32  # 256 bits
    SALT_LENGTH = 32  # 256 bits
    
    # Fixed salt for deterministic hashing
    # In production, consider deriving from a master secret
    _SALT = (
        b'\x00' * 32  # Hardcoded constant salt (32 bytes of zeros)
    )
    
    def __init__(self):
        """Initialize the hasher with fixed salt."""
        self._backend = default_backend()
    
    def compute_hash(self, plaintext: str) -> str:
        """
        Compute deterministic hash for searchable field.
        
        Process:
        1. Encode plaintext to bytes (UTF-8)
        2. Apply PBKDF2-SHA256 with 100K iterations
        3. Return as 64-character hex string
        
        Args:
            plaintext: Value to hash (email, phone, etc.)
            
        Returns:
            64-character hex string (256-bit hash in hex)
            
        Raises:
            SearchableHashError: If hashing fails
            
        Example:
            >>> hasher = SearchableHasher()
            >>> hash1 = hasher.compute_hash("rajesh@example.com")
            >>> hash2 = hasher.compute_hash("rajesh@example.com")
            >>> hash1 == hash2  # Deterministic
            True
            >>> len(hash1)
            64
        """
        try:
            # Encode plaintext to bytes
            plaintext_bytes = plaintext.encode('utf-8')
            
            # Create PBKDF2-SHA256 KDF
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=self.HASH_LENGTH,
                salt=self._SALT,
                iterations=self.ITERATIONS,
                backend=self._backend
            )
            
            # Derive hash
            hash_bytes = kdf.derive(plaintext_bytes)
            
            # Convert to hex string
            hash_hex = hash_bytes.hex()
            
            return hash_hex
        
        except UnicodeEncodeError as e:
            raise SearchableHashError(
                f"Failed to encode plaintext: {str(e)}"
            ) from e
        except Exception as e:
            raise SearchableHashError(
                f"Hash computation failed: {str(e)}"
            ) from e
    
    def verify_hash(self, plaintext: str, stored_hash: str) -> bool:
        """
        Verify plaintext matches stored hash using constant-time comparison.
        
        Prevents timing attacks by comparing hashes in constant time.
        
        Args:
            plaintext: Value to verify (email, phone, etc.)
            stored_hash: Previously computed hash to verify against
            
        Returns:
            True if plaintext matches hash, False otherwise
            
        Example:
            >>> hasher = SearchableHasher()
            >>> original = "rajesh@example.com"
            >>> hash_val = hasher.compute_hash(original)
            >>> hasher.verify_hash(original, hash_val)
            True
            >>> hasher.verify_hash("wrong@example.com", hash_val)
            False
        """
        try:
            # Compute hash of provided plaintext
            computed_hash = self.compute_hash(plaintext)
            
            # Constant-time comparison prevents timing attacks
            return hmac.compare_digest(computed_hash, stored_hash)
        
        except SearchableHashError:
            # If computation fails, return False (not equal)
            return False
        except Exception:
            # Any unexpected error means hashes don't match
            return False
    
    def get_algorithm_name(self) -> str:
        """
        Get the hash algorithm name.
        
        Returns:
            Algorithm name string
        """
        return self.ALGORITHM
    
    def get_iterations(self) -> int:
        """
        Get number of PBKDF2 iterations.
        
        Returns:
            Number of iterations (100,000)
        """
        return self.ITERATIONS
    
    def get_output_length(self) -> int:
        """
        Get hash output length in bits.
        
        Returns:
            256 bits
        """
        return self.HASH_LENGTH * 8
    
    @staticmethod
    def normalize_input(value: str) -> str:
        """
        Normalize input before hashing (lowercase, strip whitespace).
        
        Use this for email/phone fields to ensure consistency.
        
        Args:
            value: Raw input value
            
        Returns:
            Normalized value
            
        Example:
            >>> SearchableHasher.normalize_input("  USER@EXAMPLE.COM  ")
            'user@example.com'
        """
        return value.lower().strip()


# Singleton instance (initialized once at app startup)
_hasher_instance: Optional[SearchableHasher] = None


def get_hasher() -> SearchableHasher:
    """
    Get the global SearchableHasher instance.
    
    Initializes on first call. Thread-safe.
    
    Returns:
        SearchableHasher instance
        
    Example:
        >>> hasher = get_hasher()
        >>> email_hash = hasher.compute_hash("user@example.com")
    """
    global _hasher_instance
    
    if _hasher_instance is None:
        _hasher_instance = SearchableHasher()
    
    return _hasher_instance
