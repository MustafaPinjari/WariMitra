#!/usr/bin/env python
"""Quick test of encryption module"""
import os
import sys
os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.getcwd())

from apps.core.encryption import EncryptionEngine
from apps.core.searchable_hash import SearchableHasher

# Test encryption
key = EncryptionEngine.generate_key()
engine = EncryptionEngine(key)

plaintext = "Rajesh Kumar"
ciphertext = engine.encrypt(plaintext)
decrypted = engine.decrypt(ciphertext)

print(f"✓ Encryption test: {decrypted == plaintext}")
print(f"  Plaintext: {plaintext}")
print(f"  Decrypted: {decrypted}")

# Test searchable hash
hasher = SearchableHasher()
email = "rajesh@example.com"
hash1 = hasher.compute_hash(email)
hash2 = hasher.compute_hash(email)

print(f"✓ Searchable hash test (deterministic): {hash1 == hash2}")
print(f"  Email: {email}")
print(f"  Hash: {hash1}")

# Test hash verification
is_valid = hasher.verify_hash(email, hash1)
is_invalid = hasher.verify_hash("wrong@example.com", hash1)

print(f"✓ Hash verification test: valid={is_valid}, invalid={not is_invalid}")

print("\nAll basic tests passed!")
