from cryptography.fernet import Fernet

def encrypt_string(password: str, secret_key: str) -> str:
    fernet = Fernet(secret_key.encode())
    return fernet.encrypt(password.encode()).decode()

def decrypt_string(encrypted: str, secret_key: str) -> str:
    fernet = Fernet(secret_key.encode())
    return fernet.decrypt(encrypted.encode()).decode()