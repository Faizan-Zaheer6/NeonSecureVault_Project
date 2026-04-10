import hashlib
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

load_dotenv()

# --- PASSWORD HASHING (SHA-256: 72-byte limit se azad) ---
def get_password_hash(password: str):
    # SHA-256 hamesha stable rehta hai
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str):
    return get_password_hash(plain_password) == hashed_password

# --- JWT AUTHENTICATION ---
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_for_dev_only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- FILE ENCRYPTION (AES-256 / FERNET) ---
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key().decode()

try:
    cipher_suite = Fernet(ENCRYPTION_KEY.encode())
except Exception:
    cipher_suite = Fernet(Fernet.generate_key())

def encrypt_file(data: bytes):
    return cipher_suite.encrypt(data)

def decrypt_file(data: bytes):
    try:
        return cipher_suite.decrypt(data)
    except Exception:
        return b"Error: Decryption failed." 