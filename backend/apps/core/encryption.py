"""
Encryption Engine Module - AES-256-GCM Implementation

This module provides field-level encryption using AES-256-GCM with authenticated encryption.
All sensitive fields (PII, medical records, location data) are encrypted with this engine.

Security Properties:
- Algorithm: AES-256-GCM (Advanced Encryption Standard with Galois/Counter Mode)
- Key Size: 256 bits (32 bytes)
- Nonce: 96 bits (12 bytes), cryptographically random, unique per encryption
- Authentication: Automatic tampering detection via authentication tag
- Output: Base64-encoded (nonce + ciphertext + tag)

Usage:
    # Initialize with 32-byte key
    engine = EncryptionEngine(key=os.urandom(32))
    
    # Encrypt plaintext
    ciphertext_b64 = engine.encrypt("Rajesh Kumar")
    
    # Decrypt ciphertext
    plaintext = engine.decrypt(ciphertext_b64)
    assert plaintext == "Rajesh Kumar"
"""

import base64
import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend


class EncryptionIntegrityError(Exception):
    """
    Raised when decryption fails due to:
    - Invalid authentication tag (ciphertext tampered)
    - Invalid nonce format
    - Corrupted ciphertext
    
    This error indicates potential tampering or data corruption.
    """
    pass


class EncryptionFormatError(Exception):
    """
    Raised when encryption/decryption input format is invalid:
    - Key is wrong length (not 32 bytes)
    - Ciphertext is not valid base64
    - Plaintext encoding fails
    """
    pass


class EncryptionEngine:
    """
    AES-256-GCM encryption engine with authenticated encryption.
    
    Uses AEAD (Authenticated Encryption with Associated Data) to provide:
    1. Confidentiality: Data is encrypted with AES-256
    2. Authenticity: Authentication tag detects any tampering
    3. Integrity: Any bit flip in ciphertext will cause decryption failure
    
    Thread-safe after initialization (immutable key).
    """
    
    # GCM mode parameters (fixed by standard)
    NONCE_LENGTH = 12  # 96 bits - optimal for GCM
    TAG_LENGTH = 16    # 128 bits - standard authentication tag
    KEY_LENGTH = 32    # 256 bits for AES-256
    
    ALGORITHM = "AES-256-GCM"
    
    def __init__(self, key: bytes):
        """
        Initialize encryption engine with a 256-bit key.
        
        Args:
            key: 32-byte (256-bit) encryption key
            
        Raises:
            EncryptionFormatError: If key is not exactly 32 bytes
            
        Example:
            >>> import os
            >>> key = os.urandom(32)  # Generate random 256-bit key
            >>> engine = EncryptionEngine(key)
        """
        if not isinstance(key, bytes):
            raise EncryptionFormatError(
                f"Key must be bytes, got {type(key).__name__}"
            )
        
        if len(key) != self.KEY_LENGTH:
            raise EncryptionFormatError(
                f"Key must be {self.KEY_LENGTH} bytes (256 bits), "
                f"got {len(key)} bytes"
            )
        
        self.key = key
        self._backend = default_backend()
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using AES-256-GCM.
        
        Process:
        1. Generate random 96-bit nonce (unique per encryption)
        2. Encrypt plaintext with nonce using AES-256-GCM
        3. GCM automatically generates 128-bit authentication tag
        4. Return base64-encoded (nonce + ciphertext + tag)
        
        Args:
            plaintext: String to encrypt (any UTF-8 text)
            
        Returns:
            Base64-encoded ciphertext string containing:
            - 12 bytes nonce (random)
            - N bytes encrypted data
            - 16 bytes authentication tag
            
        Raises:
            EncryptionFormatError: If plaintext encoding fails
            
        Example:
            >>> engine = EncryptionEngine(os.urandom(32))
            >>> ct = engine.encrypt("Secret message")
            >>> len(ct) > 0
            True
            >>> # Ciphertext is different each time (random nonce)
            >>> ct2 = engine.encrypt("Secret message")
            >>> ct != ct2
            True
        """
        try:
            # Generate random nonce for this encryption
            # New nonce for every encryption ensures IND-CPA security
            nonce = os.urandom(self.NONCE_LENGTH)
            
            # Create cipher with key
            cipher = AESGCM(self.key)
            
            # Encode plaintext to bytes
            plaintext_bytes = plaintext.encode('utf-8')
            
            # Encrypt: GCM includes authentication tag automatically
            # The tag is appended by cryptography library
            ciphertext = cipher.encrypt(nonce, plaintext_bytes, None)
            
            # Combine nonce + ciphertext (which includes tag)
            combined = nonce + ciphertext
            
            # Return as base64 for safe storage/transmission
            return base64.b64encode(combined).decode('ascii')
        
        except UnicodeEncodeError as e:
            raise EncryptionFormatError(
                f"Failed to encode plaintext: {str(e)}"
            ) from e
        except Exception as e:
            raise EncryptionFormatError(
                f"Encryption failed: {str(e)}"
            ) from e
    
    def decrypt(self, ciphertext_b64: str) -> str:
        """
        Decrypt AES-256-GCM ciphertext.
        
        Process:
        1. Decode base64 to get nonce + ciphertext + tag
        2. Extract nonce (first 12 bytes)
        3. Decrypt with nonce using AES-256-GCM
        4. GCM verifies authentication tag (detects tampering)
        5. Return plaintext
        
        Args:
            ciphertext_b64: Base64-encoded ciphertext from encrypt()
            
        Returns:
            Decrypted plaintext string
            
        Raises:
            EncryptionIntegrityError: If authentication tag verification fails
                (indicates tampering or corruption)
            EncryptionFormatError: If ciphertext format is invalid
            
        Example:
            >>> engine = EncryptionEngine(os.urandom(32))
            >>> ct = engine.encrypt("Hello World")
            >>> plaintext = engine.decrypt(ct)
            >>> plaintext
            'Hello World'
            
            >>> # Tampered ciphertext will fail
            >>> tampered = ct[:-5] + "xxxxx"
            >>> try:
            ...     engine.decrypt(tampered)
            ... except EncryptionIntegrityError:
            ...     print("Tampering detected!")
            Tampering detected!
        """
        try:
            # Decode from base64
            try:
                combined = base64.b64decode(ciphertext_b64.encode('ascii'))
            except Exception as e:
                raise EncryptionFormatError(
                    f"Invalid base64 ciphertext: {str(e)}"
                ) from e
            
            # Validate minimum length (nonce + tag)
            if len(combined) < self.NONCE_LENGTH + self.TAG_LENGTH:
                raise EncryptionFormatError(
                    f"Ciphertext too short: {len(combined)} bytes "
                    f"(minimum {self.NONCE_LENGTH + self.TAG_LENGTH})"
                )
            
            # Extract nonce (first 12 bytes)
            nonce = combined[:self.NONCE_LENGTH]
            
            # Extract ciphertext + tag (remainder)
            ciphertext = combined[self.NONCE_LENGTH:]
            
            # Create cipher with key
            cipher = AESGCM(self.key)
            
            # Decrypt with authentication tag verification
            # If tag verification fails, cryptography raises InvalidTag
            try:
                plaintext_bytes = cipher.decrypt(nonce, ciphertext, None)
            except Exception as e:
                # InvalidTag means tampering or wrong key
                raise EncryptionIntegrityError(
                    f"Decryption failed: authentication tag verification failed. "
                    f"Data may be tampered or corrupted: {str(e)}"
                ) from e
            
            # Decode bytes to string
            plaintext = plaintext_bytes.decode('utf-8')
            
            return plaintext
        
        except (EncryptionIntegrityError, EncryptionFormatError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise EncryptionIntegrityError(
                f"Unexpected decryption error: {str(e)}"
            ) from e
    
    def verify_key_format(self) -> bool:
        """
        Verify that the current key is valid (256-bit).
        
        Returns:
            True if key is exactly 32 bytes, False otherwise
            
        Example:
            >>> key = os.urandom(32)
            >>> engine = EncryptionEngine(key)
            >>> engine.verify_key_format()
            True
        """
        return isinstance(self.key, bytes) and len(self.key) == self.KEY_LENGTH
    
    def get_key_length_bits(self) -> int:
        """
        Get the key length in bits.
        
        Returns:
            256 (AES-256)
            
        Example:
            >>> engine = EncryptionEngine(os.urandom(32))
            >>> engine.get_key_length_bits()
            256
        """
        return len(self.key) * 8
    
    @staticmethod
    def generate_key() -> bytes:
        """
        Generate a cryptographically random 256-bit encryption key.
        
        Returns:
            32 random bytes suitable for AES-256
            
        Example:
            >>> key = EncryptionEngine.generate_key()
            >>> len(key)
            32
            >>> # Use the key to initialize engine
            >>> engine = EncryptionEngine(key)
        """
        return os.urandom(32)
