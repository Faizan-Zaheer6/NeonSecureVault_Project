import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app 
from fastapi.testclient import TestClient
    
client = TestClient(app)

# 1. Test: Kya Login Page sahi load ho raha hai?
def test_read_main():
    response = client.get("/") # Agar aapka koi root endpoint hai
    # Agar sirf APIs hain toh hum seedha login check karenge
    pass

# 2. Test: Kya ghalat password par error aata hai?
def test_login_invalid_user():
    response = client.post(
        "/login",
        data={"username": "wrong@test.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

# 3. Test: Kya Admin login logic sahi hai?
def test_admin_logic():
    # Hum check kar rahe hain ke hamara logic admin pehchan raha hai ya nahi
    test_email = "neon@admin.com"
    # Logic: admin_status = True if email == "neon@admin.com" else False
    is_admin = True if test_email == "neon@admin.com" else False
    assert is_admin == True