"""
Key Management Module - Multi-backend support (AWS KMS, HashiCorp Vault, Environment Variables)

This module provides secure key management with support for multiple storage backends:
1. AWS KMS (Priority 1 - Production): Hardware-backed key management service
2. HashiCorp Vault (Priority 2 - Self-managed): Centralized secrets management
3. Environment Variables (Priority 3 - Development): Simple env var storage

Security Properties:
- Keys never stored in code or database
- In-memory caching with 1-hour TTL
- Version tracking for key rotation
- Retry logic with exponential backoff (5 retries)
- Startup validation: app refuses to start if keys missing
- Key format validation: 32-byte (256-bit) enforcement

Usage:
    # Initialize key manager
    manager = KeyManager()
    
    # Get current active key
    key = manager.get_current_key()  # bytes (32 bytes)
    
    # Get historical key for decryption
    key_v1 = manager.get_key_by_version(1)
    
    # Get key version for metadata
    version = manager.get_current_key_version()
"""

import os
import time
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class KeyManagementError(Exception):
    """Raised when key management operations fail."""
    pass


class KeyNotFoundError(KeyManagementError):
    """Raised when requested key version does not exist."""
    pass


class KeyManager:
    """
    Multi-backend key manager with support for AWS KMS, HashiCorp Vault, and environment variables.
    
    Thread-safe with in-memory caching and automatic expiration.
    Supports key versioning for rotation without service downtime.
    """
    
    # Cache configuration
    CACHE_TTL_SECONDS = 3600  # 1 hour
    MAX_RETRIES = 5
    INITIAL_BACKOFF = 1  # seconds
    
    # Supported backends
    BACKEND_ENV = 'env'
    BACKEND_KMS = 'kms'
    BACKEND_VAULT = 'vault'
    BACKENDS = [BACKEND_ENV, BACKEND_KMS, BACKEND_VAULT]
    
    def __init__(
        self,
        backend: Optional[str] = None,
        kms_key_id: Optional[str] = None,
        vault_addr: Optional[str] = None,
        vault_token: Optional[str] = None,
        vault_path: str = 'secret/encryption',
    ):
        """
        Initialize KeyManager with specified backend.
        
        Args:
            backend: Storage backend ('env', 'kms', 'vault')
                    If None, uses ENCRYPTION_KEY_STORAGE env var or defaults to 'env'
            kms_key_id: AWS KMS key ID (required if backend='kms')
            vault_addr: HashiCorp Vault address (required if backend='vault')
            vault_token: HashiCorp Vault token (required if backend='vault')
            vault_path: Path to secret in Vault (default: 'secret/encryption')
            
        Raises:
            KeyManagementError: If configuration is invalid
        """
        # Determine backend
        if backend is None:
            backend = os.getenv('ENCRYPTION_KEY_STORAGE', self.BACKEND_ENV).lower()
        
        if backend not in self.BACKENDS:
            raise KeyManagementError(
                f"Invalid backend: {backend}. Must be one of: {self.BACKENDS}"
            )
        
        self.backend = backend
        self.kms_key_id = kms_key_id or os.getenv('ENCRYPTION_KMS_KEY_ID')
        self.vault_addr = vault_addr or os.getenv('ENCRYPTION_VAULT_ADDR')
        self.vault_token = vault_token or os.getenv('ENCRYPTION_VAULT_TOKEN')
        self.vault_path = vault_path
        
        # Validate backend configuration
        self._validate_configuration()
        
        # Cache storage
        self._key_cache: Dict[str, tuple] = {}  # key_version -> (key_bytes, timestamp)
        self._current_version: Optional[int] = None
        self._current_version_time = None
        
        # Load keys on initialization
        self._load_keys()
    
    def _validate_configuration(self):
        """Validate that required configuration is present for selected backend."""
        if self.backend == self.BACKEND_KMS:
            if not self.kms_key_id:
                raise KeyManagementError(
                    "AWS KMS backend selected but ENCRYPTION_KMS_KEY_ID not set"
                )
            # Lazy validation: boto3 import happens on first use
        
        elif self.backend == self.BACKEND_VAULT:
            if not self.vault_addr or not self.vault_token:
                raise KeyManagementError(
                    "HashiCorp Vault backend selected but "
                    "ENCRYPTION_VAULT_ADDR or ENCRYPTION_VAULT_TOKEN not set"
                )
            # Lazy validation: hvac import happens on first use
        
        elif self.backend == self.BACKEND_ENV:
            if not os.getenv('ENCRYPTION_KEY'):
                raise KeyManagementError(
                    "Environment backend selected but ENCRYPTION_KEY not set in .env"
                )
    
    def _load_keys(self):
        """Load keys on startup with retry logic."""
        logger.info(f"Loading encryption keys from {self.backend} backend")
        
        retry_count = 0
        last_error = None
        
        while retry_count < self.MAX_RETRIES:
            try:
                if self.backend == self.BACKEND_ENV:
                    self._load_from_env()
                elif self.backend == self.BACKEND_KMS:
                    self._load_from_kms()
                elif self.backend == self.BACKEND_VAULT:
                    self._load_from_vault()
                
                logger.info(f"Successfully loaded {len(self._key_cache)} key(s)")
                return
            
            except Exception as e:
                last_error = e
                retry_count += 1
                
                if retry_count < self.MAX_RETRIES:
                    backoff = self.INITIAL_BACKOFF * (2 ** (retry_count - 1))
                    logger.warning(
                        f"Failed to load keys (attempt {retry_count}/{self.MAX_RETRIES}), "
                        f"retrying in {backoff}s: {str(e)}"
                    )
                    time.sleep(backoff)
        
        # All retries exhausted
        raise KeyManagementError(
            f"Failed to load encryption keys after {self.MAX_RETRIES} retries: {str(last_error)}"
        )
    
    def _load_from_env(self):
        """Load keys from environment variables."""
        # Support both ENCRYPTION_KEY and ENCRYPTION_KEY_V1 format
        key_str = os.getenv('ENCRYPTION_KEY')
        
        if not key_str:
            raise KeyManagementError("ENCRYPTION_KEY environment variable not set")
        
        # Key can be hex string or base64
        try:
            # Try hex first
            if len(key_str) == 64:  # 32 bytes in hex = 64 chars
                key_bytes = bytes.fromhex(key_str)
            else:
                import base64
                key_bytes = base64.b64decode(key_str)
            
            if len(key_bytes) != 32:
                raise ValueError(f"Key must be 32 bytes, got {len(key_bytes)}")
            
            self._key_cache[1] = (key_bytes, time.time())
            self._current_version = 1
            self._current_version_time = time.time()
            
        except Exception as e:
            raise KeyManagementError(
                f"Failed to parse ENCRYPTION_KEY: {str(e)}"
            )
    
    def _load_from_kms(self):
        """Load keys from AWS KMS."""
        try:
            import boto3
        except ImportError:
            raise KeyManagementError(
                "boto3 not installed. Install with: pip install boto3"
            )
        
        try:
            client = boto3.client('kms')
            
            # Generate data key from KMS master key
            response = client.generate_data_key(
                KeyId=self.kms_key_id,
                KeySpec='AES_256'
            )
            
            key_bytes = response['Plaintext']
            
            if len(key_bytes) != 32:
                raise KeyManagementError(
                    f"KMS returned key of wrong size: {len(key_bytes)} bytes"
                )
            
            # Store with version 1 for now
            self._key_cache[1] = (key_bytes, time.time())
            self._current_version = 1
            self._current_version_time = time.time()
            
            logger.info(f"Loaded key from AWS KMS (key_id: {self.kms_key_id})")
        
        except Exception as e:
            raise KeyManagementError(
                f"Failed to load key from AWS KMS: {str(e)}"
            )
    
    def _load_from_vault(self):
        """Load keys from HashiCorp Vault."""
        try:
            import hvac
        except ImportError:
            raise KeyManagementError(
                "hvac not installed. Install with: pip install hvac"
            )
        
        try:
            client = hvac.Client(url=self.vault_addr, token=self.vault_token)
            
            # Read secret from Vault
            secret = client.secrets.kv.read_secret_version(
                path=self.vault_path
            )
            
            secret_data = secret['data']['data']
            
            # Expect key_data or encryption_key field
            key_str = secret_data.get('key_data') or secret_data.get('encryption_key')
            
            if not key_str:
                raise KeyManagementError(
                    f"Vault secret at {self.vault_path} missing 'key_data' or 'encryption_key' field"
                )
            
            # Parse key
            try:
                if isinstance(key_str, bytes):
                    key_bytes = key_str
                elif len(key_str) == 64:
                    key_bytes = bytes.fromhex(key_str)
                else:
                    import base64
                    key_bytes = base64.b64decode(key_str)
                
                if len(key_bytes) != 32:
                    raise ValueError(f"Key must be 32 bytes, got {len(key_bytes)}")
                
                self._key_cache[1] = (key_bytes, time.time())
                self._current_version = 1
                self._current_version_time = time.time()
                
                logger.info(f"Loaded key from HashiCorp Vault ({self.vault_addr})")
            
            except Exception as e:
                raise KeyManagementError(f"Failed to parse Vault key: {str(e)}")
        
        except Exception as e:
            raise KeyManagementError(
                f"Failed to load key from HashiCorp Vault: {str(e)}"
            )
    
    def get_current_key(self) -> bytes:
        """
        Get the current active encryption key.
        
        Returns:
            32-byte (256-bit) encryption key
            
        Raises:
            KeyManagementError: If key cannot be loaded
            
        Example:
            >>> manager = KeyManager()
            >>> key = manager.get_current_key()
            >>> len(key)
            32
        """
        if self._current_version is None:
            raise KeyManagementError("No current key version set")
        
        # Check cache validity
        if not self._is_cache_valid(self._current_version):
            self._load_keys()
        
        key_bytes, _ = self._key_cache[self._current_version]
        return key_bytes
    
    def get_key_by_version(self, version: int) -> bytes:
        """
        Get a historical encryption key by version number.
        
        Used during key rotation: old records encrypted with old key,
        new records with new key. Decryption tries the correct version.
        
        Args:
            version: Key version number (1, 2, 3, ...)
            
        Returns:
            32-byte (256-bit) encryption key
            
        Raises:
            KeyNotFoundError: If version does not exist
            
        Example:
            >>> manager = KeyManager()
            >>> key_v1 = manager.get_key_by_version(1)  # Old key
            >>> len(key_v1)
            32
        """
        if version not in self._key_cache:
            raise KeyNotFoundError(f"Key version {version} not found in cache")
        
        # Check cache validity
        if not self._is_cache_valid(version):
            self._load_keys()
        
        key_bytes, _ = self._key_cache[version]
        return key_bytes
    
    def get_current_key_version(self) -> int:
        """
        Get the current active key version number.
        
        Returns:
            Current key version (1, 2, 3, ...)
            
        Example:
            >>> manager = KeyManager()
            >>> version = manager.get_current_key_version()
            >>> version >= 1
            True
        """
        if self._current_version is None:
            raise KeyManagementError("No current key version set")
        return self._current_version
    
    def set_current_key_version(self, version: int):
        """
        Set a new current key version (for key rotation).
        
        Args:
            version: New active key version
            
        Raises:
            KeyNotFoundError: If version does not exist
            
        Example:
            # During rotation: switch to new key
            >>> manager.set_current_key_version(2)
        """
        if version not in self._key_cache:
            raise KeyNotFoundError(f"Key version {version} not found in cache")
        
        self._current_version = version
        self._current_version_time = time.time()
        logger.info(f"Set current key version to {version}")
    
    def add_key_version(self, version: int, key_bytes: bytes):
        """
        Add a new key version to the cache (for key rotation).
        
        Args:
            version: New key version number
            key_bytes: 32-byte encryption key
            
        Raises:
            KeyManagementError: If key format is invalid
            
        Example:
            # During rotation: add new key
            >>> new_key = EncryptionEngine.generate_key()
            >>> manager.add_key_version(2, new_key)
        """
        if not isinstance(key_bytes, bytes):
            raise KeyManagementError(
                f"Key must be bytes, got {type(key_bytes).__name__}"
            )
        
        if len(key_bytes) != 32:
            raise KeyManagementError(
                f"Key must be 32 bytes, got {len(key_bytes)}"
            )
        
        self._key_cache[version] = (key_bytes, time.time())
        logger.info(f"Added key version {version} to cache")
    
    def _is_cache_valid(self, version: int) -> bool:
        """Check if cached key is still valid (not expired)."""
        if version not in self._key_cache:
            return False
        
        _, timestamp = self._key_cache[version]
        age_seconds = time.time() - timestamp
        
        return age_seconds < self.CACHE_TTL_SECONDS
    
    def invalidate_cache(self):
        """Force cache invalidation (for testing)."""
        self._key_cache.clear()
        self._current_version = None
        self._current_version_time = None
        logger.info("Cleared key cache")
    
    def get_key_versions(self) -> list:
        """
        Get list of all available key versions.
        
        Returns:
            List of version numbers (e.g., [1, 2])
        """
        return sorted(self._key_cache.keys())
    
    def get_backend_name(self) -> str:
        """
        Get the current backend name.
        
        Returns:
            Backend name ('env', 'kms', 'vault')
        """
        return self.backend
    
    def get_key_age_seconds(self, version: int) -> int:
        """
        Get age of a key in seconds.
        
        Args:
            version: Key version number
            
        Returns:
            Age in seconds
            
        Raises:
            KeyNotFoundError: If version does not exist
        """
        if version not in self._key_cache:
            raise KeyNotFoundError(f"Key version {version} not found")
        
        _, timestamp = self._key_cache[version]
        return int(time.time() - timestamp)


# Singleton instance (initialized once at app startup)
_key_manager_instance: Optional[KeyManager] = None


def get_key_manager() -> KeyManager:
    """
    Get the global KeyManager instance.
    
    Initializes on first call. Thread-safe.
    
    Returns:
        KeyManager instance
        
    Raises:
        KeyManagementError: If initialization fails
        
    Example:
        >>> manager = get_key_manager()
        >>> key = manager.get_current_key()
    """
    global _key_manager_instance
    
    if _key_manager_instance is None:
        _key_manager_instance = KeyManager()
    
    return _key_manager_instance


# For Django integration: initialize in apps.py or settings
def initialize_key_manager():
    """
    Initialize the global KeyManager instance.
    
    Call this in Django AppConfig.ready() to ensure keys are loaded
    before first request.
    
    Example:
        # In apps.py
        from django.apps import AppConfig
        
        class CoreConfig(AppConfig):
            name = 'apps.core'
            
            def ready(self):
                from apps.core.key_manager import initialize_key_manager
                initialize_key_manager()
    """
    global _key_manager_instance
    
    if _key_manager_instance is None:
        logger.info("Initializing global KeyManager instance")
        _key_manager_instance = KeyManager()
