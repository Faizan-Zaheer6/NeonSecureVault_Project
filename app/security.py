from passlib.context import CryptContext
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

# Environment variables load karein
load_dotenv()

# Password Hashing Setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    # Bcrypt 72-byte limit fix (Safely handling long passwords)
    encoded_pass = password.encode("utf-8")
    if len(encoded_pass) > 72:
        password = encoded_pass[:72].decode("utf-8", "ignore")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    encoded_plain = plain_password.encode("utf-8")
    if len(encoded_plain) > 72:
        plain_password = encoded_plain[:72].decode("utf-8", "ignore")
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

# =========================
# JWT AUTHENTICATION
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_for_dev_only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

# =========================
# FILE ENCRYPTION (FERNET)
# =========================
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# Agar .env mein key nahi milti ya ghalat hai toh server crash hone se bachane ka logic
if not ENCRYPTION_KEY:

    print("⚠️ WARNING: ENCRYPTION_KEY not found in .env. Using temporary key.")
    ENCRYPTION_KEY = Fernet.generate_key().decode()

try:
    # Fernet key strictly 32-byte base64 encoded honi chahiye
    cipher_suite = Fernet(ENCRYPTION_KEY.encode())
except Exception as e:
    # Agar key ghalat format mein hai (ValueError fix)
    print(f"❌ Encryption Error: {str(e)}")
    # Fallback key taake server chalta rahe
    dummy_key = Fernet.generate_key()
    cipher_suite = Fernet(dummy_key)

def encrypt_file(data: bytes):
    return cipher_suite.encrypt(data)

def decrypt_file(data: bytes):
    try:
        return cipher_suite.decrypt(data)
    except Exception:
        # Agar key badal jaye toh purani files decrypt nahi hongi
        return b"Error: Decryption failed. Possible key mismatch."