#!/usr/bin/env python3
"""
AES File Encryptor/Decryptor GUI
Simple graphical interface for encrypting and decrypting .aes files.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from pathlib import Path
import threading
from typing import Optional
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
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
            if len(data) >= 32:
                result = self._try_format_with_salt_iv(data, password)
                if result:
                    return result

            if len(data) >= 16:
                result = self._try_format_with_iv_only(data, password)
                if result:
                    return result

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

            key = PBKDF2(password, salt, dkLen=32, count=100000, hmac_hash_module=SHA256)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            plaintext = cipher.decrypt(ciphertext)
            plaintext = self._unpad(plaintext)

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

            key = hashlib.sha256(password.encode()).digest()
            cipher = AES.new(key, AES.MODE_CBC, iv)
            plaintext = cipher.decrypt(ciphertext)
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

            key_iv = self._derive_key_and_iv(password.encode(), salt, 32, 16)
            key = key_iv[:32]
            iv = key_iv[32:48]

            cipher = AES.new(key, AES.MODE_CBC, iv)
            plaintext = cipher.decrypt(ciphertext)
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

        for i in range(1, padding_length + 1):
            if data[-i] != padding_length:
                raise ValueError("Invalid padding")

        return data[:-padding_length]

    def _is_valid_data(self, data: bytes) -> bool:
        """Basic heuristic to check if decrypted data is valid."""
        if len(data) == 0:
            return False

        try:
            data.decode('utf-8')
            return True
        except:
            pass

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

        printable = sum(1 for b in data[:min(100, len(data))] if 32 <= b <= 126 or b in [9, 10, 13])
        if printable / min(100, len(data)) > 0.9:
            return True

        return True


class AESEncryptor:
    """Handles AES file encryption."""

    @staticmethod
    def encrypt_file(input_file: str, password: str) -> bytes:
        """
        Encrypt a file with a password using AES-256-CBC with PBKDF2.
        Returns the encrypted data as bytes.
        """
        # Read the input file
        with open(input_file, 'rb') as f:
            plaintext = f.read()

        # Generate random salt and IV
        salt = get_random_bytes(16)
        iv = get_random_bytes(16)

        # Derive key using PBKDF2
        key = PBKDF2(password, salt, dkLen=32, count=100000, hmac_hash_module=SHA256)

        # Pad the plaintext
        padded_plaintext = AESEncryptor._pad(plaintext)

        # Encrypt
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(padded_plaintext)

        # Return salt + IV + ciphertext
        return salt + iv + ciphertext

    @staticmethod
    def _pad(data: bytes) -> bytes:
        """Add PKCS7 padding."""
        padding_length = 16 - (len(data) % 16)
        padding = bytes([padding_length]) * padding_length
        return data + padding


class AESDecryptorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AES File Encryptor/Decryptor")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        self.input_file = None
        self.password_file = None
        self.passwords = []
        self.is_running = False
        self.mode = "decrypt"  # "encrypt" or "decrypt"

        self.create_widgets()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Mode Selection
        mode_frame = ttk.LabelFrame(main_frame, text="Mode", padding="10")
        mode_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        self.mode_var = tk.StringVar(value="decrypt")
        ttk.Radiobutton(mode_frame, text="Decrypt File (try passwords)", variable=self.mode_var,
                       value="decrypt", command=self.toggle_mode).grid(row=0, column=0, padx=(0, 20))
        ttk.Radiobutton(mode_frame, text="Encrypt File (single password)", variable=self.mode_var,
                       value="encrypt", command=self.toggle_mode).grid(row=0, column=1)

        # File Selection
        self.file_label = ttk.Label(main_frame, text="Input File:", font=('Arial', 10, 'bold'))
        self.file_label.grid(row=1, column=0, sticky=tk.W, pady=5)

        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)

        self.file_entry = ttk.Entry(file_frame, width=50)
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        ttk.Button(file_frame, text="Browse", command=self.browse_input_file).grid(row=0, column=1)

        # Password Input Method
        self.password_method_label = ttk.Label(main_frame, text="Password Method:", font=('Arial', 10, 'bold'))
        self.password_method_label.grid(row=3, column=0, sticky=tk.W, pady=(10, 5))

        self.method_var = tk.StringVar(value="file")

        self.method_frame = ttk.Frame(main_frame)
        self.method_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        self.method_file_radio = ttk.Radiobutton(self.method_frame, text="From File", variable=self.method_var,
                       value="file", command=self.toggle_method)
        self.method_file_radio.grid(row=0, column=0, padx=(0, 20))

        self.method_manual_radio = ttk.Radiobutton(self.method_frame, text="Enter Manually", variable=self.method_var,
                       value="manual", command=self.toggle_method)
        self.method_manual_radio.grid(row=0, column=1)

        # Password File Selection
        self.password_file_frame = ttk.Frame(main_frame)
        self.password_file_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        self.password_file_frame.columnconfigure(0, weight=1)

        self.password_file_entry = ttk.Entry(self.password_file_frame, width=50)
        self.password_file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        ttk.Button(self.password_file_frame, text="Browse", command=self.browse_password_file).grid(row=0, column=1)

        # Manual Password Entry
        self.manual_password_frame = ttk.Frame(main_frame)
        self.manual_password_frame.columnconfigure(0, weight=1)

        self.password_label = ttk.Label(self.manual_password_frame, text="Enter passwords (one per line):")
        self.password_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.password_text = scrolledtext.ScrolledText(self.manual_password_frame, height=8, width=50)
        self.password_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Start Button
        self.start_button = ttk.Button(main_frame, text="Start Decryption", command=self.start_operation)
        self.start_button.grid(row=6, column=0, columnspan=3, pady=10)

        # Progress
        ttk.Label(main_frame, text="Progress:", font=('Arial', 10, 'bold')).grid(row=7, column=0, sticky=tk.W, pady=(10, 5))

        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=8, column=0, columnspan=3, sticky=tk.W)

        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 10))

        # Log Output
        ttk.Label(main_frame, text="Log:", font=('Arial', 10, 'bold')).grid(row=10, column=0, sticky=tk.W, pady=(10, 5))

        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, width=50, state='disabled')
        self.log_text.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

        main_frame.rowconfigure(11, weight=1)

        # Initial toggle
        self.toggle_mode()
        self.toggle_method()

    def toggle_mode(self):
        """Toggle between encrypt and decrypt modes."""
        mode = self.mode_var.get()
        self.mode = mode

        if mode == "encrypt":
            self.start_button.config(text="Encrypt File")
            self.file_label.config(text="File to Encrypt:")
            self.password_method_label.config(text="Password:")
            self.method_file_radio.config(state='disabled')
            self.method_var.set("manual")
            self.password_label.config(text="Enter password:")
            self.password_text.config(height=2)
        else:
            self.start_button.config(text="Start Decryption")
            self.file_label.config(text="AES File to Decrypt:")
            self.password_method_label.config(text="Password Method:")
            self.method_file_radio.config(state='normal')
            self.password_label.config(text="Enter passwords (one per line):")
            self.password_text.config(height=8)

        self.toggle_method()

    def toggle_method(self):
        """Toggle between file and manual password entry."""
        if self.method_var.get() == "file" and self.mode == "decrypt":
            self.password_file_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
            self.manual_password_frame.grid_remove()
        else:
            self.password_file_frame.grid_remove()
            self.manual_password_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

    def browse_input_file(self):
        """Browse for input file."""
        if self.mode == "encrypt":
            filename = filedialog.askopenfilename(
                title="Select File to Encrypt",
                filetypes=[("All Files", "*.*")]
            )
        else:
            filename = filedialog.askopenfilename(
                title="Select AES File to Decrypt",
                filetypes=[("AES Files", "*.aes"), ("All Files", "*.*")]
            )

        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            self.input_file = filename

    def browse_password_file(self):
        """Browse for password file."""
        filename = filedialog.askopenfilename(
            title="Select Password File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filename:
            self.password_file_entry.delete(0, tk.END)
            self.password_file_entry.insert(0, filename)
            self.password_file = filename

    def log(self, message):
        """Add message to log."""
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')

    def show_success_dialog(self, password: str, output_file: str):
        """Show success dialog with password and copy button."""
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Decryption Successful")
        dialog.geometry("450x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Success message
        ttk.Label(main_frame, text="File decrypted successfully!",
                 font=('Arial', 12, 'bold')).pack(pady=(0, 10))

        # Password frame
        password_frame = ttk.LabelFrame(main_frame, text="Password", padding="10")
        password_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Password display
        password_entry = ttk.Entry(password_frame, width=40, font=('Courier', 10))
        password_entry.insert(0, password)
        password_entry.config(state='readonly')
        password_entry.pack(side=tk.LEFT, padx=(0, 5))

        # Copy button
        def copy_to_clipboard():
            dialog.clipboard_clear()
            dialog.clipboard_append(password)
            dialog.update()
            copy_btn.config(text="Copied!")
            dialog.after(1500, lambda: copy_btn.config(text="Copy"))

        copy_btn = ttk.Button(password_frame, text="Copy", command=copy_to_clipboard, width=8)
        copy_btn.pack(side=tk.LEFT)

        # File location
        ttk.Label(main_frame, text=f"Saved to:\n{output_file}",
                 wraplength=400, justify=tk.CENTER).pack(pady=(0, 10))

        # OK button
        ok_btn = ttk.Button(main_frame, text="OK", command=dialog.destroy, width=10)
        ok_btn.pack(pady=(10, 0))

        # Focus on OK button
        ok_btn.focus_set()

    def start_operation(self):
        """Start encryption or decryption."""
        if self.is_running:
            messagebox.showwarning("Warning", "Operation is already running!")
            return

        # Validate inputs
        self.input_file = self.file_entry.get()
        if not self.input_file:
            messagebox.showerror("Error", "Please select a file!")
            return

        if not Path(self.input_file).exists():
            messagebox.showerror("Error", "File does not exist!")
            return

        # Clear log
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')

        if self.mode == "encrypt":
            # For encryption, get single password
            password_text = self.password_text.get("1.0", tk.END).strip()
            if not password_text:
                messagebox.showerror("Error", "Please enter a password!")
                return

            self.is_running = True
            self.start_button.configure(state='disabled')
            thread = threading.Thread(target=self.encrypt_file, args=(password_text,), daemon=True)
            thread.start()
        else:
            # For decryption, get password list
            if self.method_var.get() == "file":
                self.password_file = self.password_file_entry.get()
                if not self.password_file:
                    messagebox.showerror("Error", "Please select a password file!")
                    return

                try:
                    with open(self.password_file, 'r', encoding='utf-8', errors='ignore') as f:
                        self.passwords = [line.strip() for line in f if line.strip()]
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read password file: {e}")
                    return
            else:
                password_text = self.password_text.get("1.0", tk.END)
                self.passwords = [line.strip() for line in password_text.split('\n') if line.strip()]

            if not self.passwords:
                messagebox.showerror("Error", "No passwords provided!")
                return

            self.is_running = True
            self.start_button.configure(state='disabled')
            thread = threading.Thread(target=self.decrypt_file, daemon=True)
            thread.start()

    def encrypt_file(self, password: str):
        """Encrypt the file with the given password."""
        try:
            self.log(f"Starting encryption of: {self.input_file}")
            self.progress_var.set("Encrypting file...")
            self.progress_bar['value'] = 50

            # Encrypt the file
            encrypted_data = AESEncryptor.encrypt_file(self.input_file, password)

            self.progress_bar['value'] = 75

            # Ask where to save
            default_name = Path(self.input_file).name + ".aes"
            output_file = filedialog.asksaveasfilename(
                title="Save Encrypted File",
                initialfile=default_name,
                defaultextension=".aes",
                filetypes=[("AES Files", "*.aes"), ("All Files", "*.*")]
            )

            if output_file:
                with open(output_file, 'wb') as f:
                    f.write(encrypted_data)

                self.log(f"\nSUCCESS! File encrypted")
                self.log(f"Encrypted file saved to: {output_file}")
                self.log(f"Size: {len(encrypted_data)} bytes")
                messagebox.showinfo("Success", f"File encrypted successfully!\n\nSaved to: {output_file}")

            self.progress_var.set("Encryption successful!")
            self.progress_bar['value'] = 100

        except Exception as e:
            self.log(f"\nERROR: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.progress_var.set("Error occurred")

        finally:
            self.is_running = False
            self.start_button.configure(state='normal')

    def decrypt_file(self):
        """Decrypt the file using password list."""
        try:
            self.log(f"Starting decryption of: {self.input_file}")
            self.log(f"Trying {len(self.passwords)} passwords...")

            decryptor = AESDecryptor(self.input_file)

            for i, password in enumerate(self.passwords, 1):
                if not self.is_running:
                    break

                progress = (i / len(self.passwords)) * 100
                self.progress_bar['value'] = progress
                self.progress_var.set(f"Trying password {i}/{len(self.passwords)}: {password[:20]}...")

                result = decryptor.try_decrypt(password)

                if result is not None:
                    self.log(f"\nSUCCESS! Password found: {password}")

                    # Ask where to save - use original filename without .aes extension
                    input_path = Path(self.input_file)
                    if input_path.suffix.lower() == '.aes':
                        # Remove .aes extension to get original filename
                        default_name = input_path.stem
                    else:
                        default_name = input_path.name

                    output_file = filedialog.asksaveasfilename(
                        title="Save Decrypted File",
                        initialfile=default_name,
                        defaultextension=".*",
                        filetypes=[("All Files", "*.*")]
                    )

                    if output_file:
                        with open(output_file, 'wb') as f:
                            f.write(result)
                        self.log(f"Decrypted file saved to: {output_file}")
                        self.log(f"Size: {len(result)} bytes")

                        # Show success dialog with copy button
                        self.show_success_dialog(password, output_file)

                    self.progress_var.set("Decryption successful!")
                    self.progress_bar['value'] = 100
                    self.is_running = False
                    self.start_button.configure(state='normal')
                    return

            # No password worked
            self.log(f"\nFAILED: None of the {len(self.passwords)} passwords worked.")
            messagebox.showerror("Failed", f"Could not decrypt the file.\nNone of the {len(self.passwords)} passwords worked.")
            self.progress_var.set("Decryption failed")
            self.progress_bar['value'] = 0

        except Exception as e:
            self.log(f"\nERROR: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.progress_var.set("Error occurred")

        finally:
            self.is_running = False
            self.start_button.configure(state='normal')


def main():
    root = tk.Tk()
    app = AESDecryptorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
