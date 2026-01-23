#!/usr/bin/env python3
"""
AES File Decryptor
Attempts to decrypt .aes files using a list of possible passwords.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
import hashlib


class AESDecryptor:
    """Handles AES file decryption with password attempts."""

    def __init__(self, aes_file: str):
        self.aes_file = Path(aes_file)
        if not self.aes_file.exists():
            raise FileNotFoundError(f"File not found: {aes_file}")

    def try_decrypt(self, password: str) -> Optional[bytes]:
        """
        Attempt to decrypt the file with a given password.
        Returns decrypted data if successful, None otherwise.
        """
        try:
            with open(self.aes_file, 'rb') as f:
                data = f.read()

            # Try different common AES file formats

            # Format 1: Salt (16 bytes) + IV (16 bytes) + Ciphertext
            if len(data) >= 32:
                result = self._try_format_with_salt_iv(data, password)
                if result:
                    return result

            # Format 2: IV (16 bytes) + Ciphertext (no salt, direct password)
            if len(data) >= 16:
                result = self._try_format_with_iv_only(data, password)
                if result:
                    return result

            # Format 3: OpenSSL format (Salted__ + salt + ciphertext)
            if data.startswith(b'Salted__'):
                result = self._try_openssl_format(data, password)
                if result:
                    return result

            return None

        except Exception as e:
            return None

    def _try_format_with_salt_iv(self, data: bytes, password: str) -> Optional[bytes]:
        """Try decryption with salt and IV at the beginning."""
        try:
            salt = data[:16]
            iv = data[16:32]
            ciphertext = data[32:]

            # Derive key using PBKDF2
            key = PBKDF2(password, salt, dkLen=32, count=100000, hmac_hash_module=SHA256)

            cipher = AES.new(key, AES.MODE_CBC, iv)
            plaintext = cipher.decrypt(ciphertext)

            # Remove PKCS7 padding
            plaintext = self._unpad(plaintext)

            # Verify it's valid data (basic heuristic)
            if self._is_valid_data(plaintext):
                return plaintext

            return None
        except:
            return None

    def _try_format_with_iv_only(self, data: bytes, password: str) -> Optional[bytes]:
        """Try decryption with IV only (password hashed to key)."""
        try:
            iv = data[:16]
            ciphertext = data[16:]

            # Derive key from password using SHA256
            key = hashlib.sha256(password.encode()).digest()

            cipher = AES.new(key, AES.MODE_CBC, iv)
            plaintext = cipher.decrypt(ciphertext)

            # Remove PKCS7 padding
            plaintext = self._unpad(plaintext)

            if self._is_valid_data(plaintext):
                return plaintext

            return None
        except:
            return None

    def _try_openssl_format(self, data: bytes, password: str) -> Optional[bytes]:
        """Try OpenSSL AES-256-CBC format."""
        try:
            if not data.startswith(b'Salted__'):
                return None

            salt = data[8:16]
            ciphertext = data[16:]

            # OpenSSL EVP_BytesToKey equivalent
            key_iv = self._derive_key_and_iv(password.encode(), salt, 32, 16)
            key = key_iv[:32]
            iv = key_iv[32:48]

            cipher = AES.new(key, AES.MODE_CBC, iv)
            plaintext = cipher.decrypt(ciphertext)

            # Remove PKCS7 padding
            plaintext = self._unpad(plaintext)

            if self._is_valid_data(plaintext):
                return plaintext

            return None
        except:
            return None

    def _derive_key_and_iv(self, password: bytes, salt: bytes, key_length: int, iv_length: int) -> bytes:
        """OpenSSL's EVP_BytesToKey with MD5."""
        d = d_i = b''
        while len(d) < key_length + iv_length:
            d_i = hashlib.md5(d_i + password + salt).digest()
            d += d_i
        return d[:key_length + iv_length]

    def _unpad(self, data: bytes) -> bytes:
        """Remove PKCS7 padding."""
        padding_length = data[-1]
        if padding_length > 16 or padding_length == 0:
            raise ValueError("Invalid padding")

        # Verify all padding bytes are the same
        for i in range(1, padding_length + 1):
            if data[-i] != padding_length:
                raise ValueError("Invalid padding")

        return data[:-padding_length]

    def _is_valid_data(self, data: bytes) -> bool:
        """Basic heuristic to check if decrypted data is valid."""
        if len(data) == 0:
            return False

        # Check if it's printable text or valid binary
        try:
            # If it can decode as text, it's probably valid
            data.decode('utf-8')
            return True
        except:
            pass

        # Check for common file signatures
        signatures = [
            b'PK\x03\x04',  # ZIP
            b'\x89PNG',     # PNG
            b'\xff\xd8\xff', # JPEG
            b'GIF8',        # GIF
            b'%PDF',        # PDF
            b'\x1f\x8b',    # GZIP
        ]

        for sig in signatures:
            if data.startswith(sig):
                return True

        # If less than 10% non-printable characters, probably valid
        printable = sum(1 for b in data[:min(100, len(data))] if 32 <= b <= 126 or b in [9, 10, 13])
        if printable / min(100, len(data)) > 0.9:
            return True

        return True  # Be permissive


def load_passwords(password_file: str) -> List[str]:
    """Load passwords from a file (one per line)."""
    with open(password_file, 'r', encoding='utf-8', errors='ignore') as f:
        passwords = [line.strip() for line in f if line.strip()]
    return passwords


def main():
    parser = argparse.ArgumentParser(
        description='Decrypt AES encrypted files using a password list',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file.aes -p passwords.txt -o decrypted.txt
  %(prog)s file.aes -w password1 password2 password3
        """
    )

    parser.add_argument('aes_file', help='The .aes file to decrypt')

    password_group = parser.add_mutually_exclusive_group(required=True)
    password_group.add_argument('-p', '--password-file',
                                help='File containing passwords (one per line)')
    password_group.add_argument('-w', '--passwords', nargs='+',
                                help='List of passwords to try')

    parser.add_argument('-o', '--output',
                       help='Output file for decrypted content (default: <input>.decrypted)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show each password attempt')

    args = parser.parse_args()

    # Load passwords
    if args.password_file:
        print(f"Loading passwords from {args.password_file}...")
        passwords = load_passwords(args.password_file)
        print(f"Loaded {len(passwords)} passwords")
    else:
        passwords = args.passwords
        print(f"Trying {len(passwords)} passwords")

    # Initialize decryptor
    try:
        decryptor = AESDecryptor(args.aes_file)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Try each password
    print(f"\nAttempting to decrypt {args.aes_file}...")
    for i, password in enumerate(passwords, 1):
        if args.verbose:
            print(f"[{i}/{len(passwords)}] Trying: {password}")

        result = decryptor.try_decrypt(password)

        if result is not None:
            print(f"\n✓ Success! Password found: {password}")

            # Determine output file
            if args.output:
                output_file = args.output
            else:
                output_file = str(Path(args.aes_file).with_suffix('')) + '.decrypted'

            # Write decrypted content
            with open(output_file, 'wb') as f:
                f.write(result)

            print(f"Decrypted content saved to: {output_file}")
            print(f"Size: {len(result)} bytes")
            return 0

    print(f"\n✗ Failed to decrypt. None of the {len(passwords)} passwords worked.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
