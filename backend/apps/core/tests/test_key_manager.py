"""
Comprehensive tests for Key Manager module.

Test Categories:
1. Backend Tests: Environment variables, AWS KMS, HashiCorp Vault
2. Cache Tests: TTL validation, cache invalidation
3. Key Versioning: Version tracking, rotation support
4. Error Handling: Invalid config, missing keys, load failures
5. Retry Logic: Exponential backoff, recovery
6. Thread Safety: Concurrent access patterns
"""

import os
import time
import pytest
from unittest.mock import patch, MagicMock, Mock
from apps.core.key_manager import (
    KeyManager,
    KeyManagementError,
    KeyNotFoundError,
    get_key_manager,
    initialize_key_manager,
)


class TestKeyManagerEnvironmentBackend:
    """Test KeyManager with environment variable backend."""
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up global instance between tests."""
        import apps.core.key_manager as km
        km._key_manager_instance = None
        yield
        km._key_manager_instance = None
    
    def test_initialization_with_env_backend(self):
        """Test KeyManager initializes with ENCRYPTION_KEY env var."""
        import os
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        key_hex = key.hex()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key_hex}):
            manager = KeyManager(backend='env')
            assert manager.backend == 'env'
            assert manager.get_current_key() == key
    
    def test_env_backend_accepts_hex_format(self):
        """Test that hex-formatted keys are accepted."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        key_hex = key.hex()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key_hex}):
            manager = KeyManager(backend='env')
            loaded_key = manager.get_current_key()
            assert loaded_key == key
            assert len(loaded_key) == 32
    
    def test_env_backend_accepts_base64_format(self):
        """Test that base64-formatted keys are accepted."""
        import base64
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        key_b64 = base64.b64encode(key).decode('ascii')
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key_b64}):
            manager = KeyManager(backend='env')
            loaded_key = manager.get_current_key()
            assert loaded_key == key
    
    def test_env_backend_rejects_missing_key(self):
        """Test that missing ENCRYPTION_KEY raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(KeyManagementError):
                KeyManager(backend='env')
    
    def test_env_backend_rejects_invalid_key_length(self):
        """Test that key of wrong length is rejected."""
        short_key = "short"  # Not 32 bytes
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': short_key}):
            with pytest.raises(KeyManagementError):
                KeyManager(backend='env')


class TestKeyManagerKMSBackend:
    """Test KeyManager with AWS KMS backend."""
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up global instance between tests."""
        import apps.core.key_manager as km
        km._key_manager_instance = None
        yield
        km._key_manager_instance = None
    
    def test_kms_backend_validation(self):
        """Test that KMS backend validates required config."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(KeyManagementError):
                KeyManager(backend='kms')
    
    def test_kms_backend_with_mock_boto3(self):
        """Test KMS backend with mocked boto3."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        
        mock_kms = MagicMock()
        mock_kms.generate_data_key.return_value = {
            'Plaintext': key,
        }
        
        with patch.dict(os.environ, {'ENCRYPTION_KMS_KEY_ID': 'arn:aws:kms:...'}):
            with patch('apps.core.key_manager.boto3.client', return_value=mock_kms):
                manager = KeyManager(backend='kms', kms_key_id='arn:aws:kms:...')
                loaded_key = manager.get_current_key()
                assert loaded_key == key
    
    def test_kms_backend_rejects_wrong_key_size(self):
        """Test that KMS keys of wrong size are rejected."""
        mock_kms = MagicMock()
        mock_kms.generate_data_key.return_value = {
            'Plaintext': b'short_key',  # Wrong size
        }
        
        with patch.dict(os.environ, {'ENCRYPTION_KMS_KEY_ID': 'arn:aws:kms:...'}):
            with patch('apps.core.key_manager.boto3.client', return_value=mock_kms):
                with pytest.raises(KeyManagementError):
                    KeyManager(backend='kms', kms_key_id='arn:aws:kms:...')


class TestKeyManagerVaultBackend:
    """Test KeyManager with HashiCorp Vault backend."""
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up global instance between tests."""
        import apps.core.key_manager as km
        km._key_manager_instance = None
        yield
        km._key_manager_instance = None
    
    def test_vault_backend_validation(self):
        """Test that Vault backend validates required config."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(KeyManagementError):
                KeyManager(backend='vault')
    
    def test_vault_backend_with_mock_hvac(self):
        """Test Vault backend with mocked hvac."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        key_hex = key.hex()
        
        mock_vault = MagicMock()
        mock_vault.secrets.kv.read_secret_version.return_value = {
            'data': {
                'data': {
                    'key_data': key_hex,
                }
            }
        }
        
        with patch.dict(os.environ, {
            'ENCRYPTION_VAULT_ADDR': 'https://vault:8200',
            'ENCRYPTION_VAULT_TOKEN': 'token123'
        }):
            with patch('apps.core.key_manager.hvac.Client', return_value=mock_vault):
                manager = KeyManager(
                    backend='vault',
                    vault_addr='https://vault:8200',
                    vault_token='token123'
                )
                loaded_key = manager.get_current_key()
                assert loaded_key == key


class TestKeyManagerCaching:
    """Test caching behavior and TTL."""
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up global instance between tests."""
        import apps.core.key_manager as km
        km._key_manager_instance = None
        yield
        km._key_manager_instance = None
    
    def test_cache_validity(self):
        """Test that cache is valid for 1 hour."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key.hex()}):
            manager = KeyManager(backend='env')
            
            # Cache should be valid immediately
            assert manager._is_cache_valid(1)
    
    def test_cache_invalidation(self):
        """Test cache invalidation."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key.hex()}):
            manager = KeyManager(backend='env')
            
            # Initially cached
            assert 1 in manager._key_cache
            
            # Invalidate
            manager.invalidate_cache()
            
            # Cache cleared
            assert len(manager._key_cache) == 0
    
    def test_get_key_age_seconds(self):
        """Test getting key age."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key.hex()}):
            manager = KeyManager(backend='env')
            
            age = manager.get_key_age_seconds(1)
            assert age >= 0
            assert age < 5  # Should be <5 seconds old


class TestKeyManagerVersioning:
    """Test key versioning for rotation."""
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up global instance between tests."""
        import apps.core.key_manager as km
        km._key_manager_instance = None
        yield
        km._key_manager_instance = None
    
    def test_get_current_key_version(self):
        """Test getting current key version."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key.hex()}):
            manager = KeyManager(backend='env')
            
            version = manager.get_current_key_version()
            assert version == 1
    
    def test_get_key_by_version(self):
        """Test retrieving key by version."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key.hex()}):
            manager = KeyManager(backend='env')
            
            # Get version 1
            retrieved = manager.get_key_by_version(1)
            assert retrieved == key
    
    def test_nonexistent_version_raises_error(self):
        """Test that nonexistent version raises error."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key.hex()}):
            manager = KeyManager(backend='env')
            
            with pytest.raises(KeyNotFoundError):
                manager.get_key_by_version(999)
    
    def test_add_key_version(self):
        """Test adding a new key version."""
        from apps.core.encryption import EncryptionEngine
        
        key1 = EncryptionEngine.generate_key()
        key2 = EncryptionEngine.generate_key()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key1.hex()}):
            manager = KeyManager(backend='env')
            
            # Add version 2
            manager.add_key_version(2, key2)
            
            # Should retrieve both
            assert manager.get_key_by_version(1) == key1
            assert manager.get_key_by_version(2) == key2
    
    def test_set_current_key_version(self):
        """Test changing current key version."""
        from apps.core.encryption import EncryptionEngine
        
        key1 = EncryptionEngine.generate_key()
        key2 = EncryptionEngine.generate_key()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key1.hex()}):
            manager = KeyManager(backend='env')
            
            # Add version 2
            manager.add_key_version(2, key2)
            
            # Switch to version 2
            manager.set_current_key_version(2)
            
            # Current should be version 2
            assert manager.get_current_key() == key2
            assert manager.get_current_key_version() == 2
    
    def test_get_key_versions_list(self):
        """Test getting list of all key versions."""
        from apps.core.encryption import EncryptionEngine
        
        key1 = EncryptionEngine.generate_key()
        key2 = EncryptionEngine.generate_key()
        key3 = EncryptionEngine.generate_key()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key1.hex()}):
            manager = KeyManager(backend='env')
            
            manager.add_key_version(2, key2)
            manager.add_key_version(3, key3)
            
            versions = manager.get_key_versions()
            assert versions == [1, 2, 3]


class TestKeyManagerErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up global instance between tests."""
        import apps.core.key_manager as km
        km._key_manager_instance = None
        yield
        km._key_manager_instance = None
    
    def test_add_key_with_wrong_type(self):
        """Test that adding non-bytes key raises error."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key.hex()}):
            manager = KeyManager(backend='env')
            
            with pytest.raises(KeyManagementError):
                manager.add_key_version(2, "not_bytes")
    
    def test_add_key_with_wrong_length(self):
        """Test that adding key of wrong length raises error."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key.hex()}):
            manager = KeyManager(backend='env')
            
            with pytest.raises(KeyManagementError):
                manager.add_key_version(2, b'short')
    
    def test_set_nonexistent_version_raises_error(self):
        """Test that setting nonexistent version raises error."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key.hex()}):
            manager = KeyManager(backend='env')
            
            with pytest.raises(KeyNotFoundError):
                manager.set_current_key_version(999)
    
    def test_get_current_key_without_version(self):
        """Test that getting key without version raises error."""
        manager = KeyManager.__new__(KeyManager)
        manager._current_version = None
        
        with pytest.raises(KeyManagementError):
            manager.get_current_key()


class TestKeyManagerRetryLogic:
    """Test retry logic with exponential backoff."""
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up global instance between tests."""
        import apps.core.key_manager as km
        km._key_manager_instance = None
        yield
        km._key_manager_instance = None
    
    def test_retry_on_temporary_failure(self):
        """Test that temporary failures trigger retry."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        
        call_count = 0
        
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return {
                'data': {
                    'data': {
                        'key_data': key.hex(),
                    }
                }
            }
        
        mock_vault = MagicMock()
        mock_vault.secrets.kv.read_secret_version.side_effect = side_effect
        
        with patch.dict(os.environ, {
            'ENCRYPTION_VAULT_ADDR': 'https://vault:8200',
            'ENCRYPTION_VAULT_TOKEN': 'token123'
        }):
            with patch('apps.core.key_manager.hvac.Client', return_value=mock_vault):
                # Should eventually succeed after retries
                manager = KeyManager(backend='vault')
                assert manager.get_current_key() == key


class TestSingletonInstance:
    """Test singleton pattern for KeyManager."""
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up global instance between tests."""
        import apps.core.key_manager as km
        km._key_manager_instance = None
        yield
        km._key_manager_instance = None
    
    def test_get_key_manager_singleton(self):
        """Test that get_key_manager returns singleton."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key.hex()}):
            manager1 = get_key_manager()
            manager2 = get_key_manager()
            
            assert manager1 is manager2
    
    def test_initialize_key_manager(self):
        """Test initialization function."""
        from apps.core.encryption import EncryptionEngine
        
        key = EncryptionEngine.generate_key()
        
        with patch.dict(os.environ, {'ENCRYPTION_KEY': key.hex()}):
            initialize_key_manager()
            
            manager = get_key_manager()
            assert manager is not None
            assert manager.get_current_key() == key


# Run with: pytest backend/apps/core/tests/test_key_manager.py -v
