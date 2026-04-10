from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Response, status
from sqlalchemy.orm import Session
from . import models, auth, database, security, schemas
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI(title="NeonSecureVault Pro")

# --- 1. MIDDLEWARE (CORS) ---
# Frontend aur Backend ke darmiyan security bridge
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database tables ko startup par hi ensure karna
models.Base.metadata.create_all(bind=database.engine)

# --- 2. SECURITY HELPER: Admin Clearance ---
def check_admin(current_user: models.User = Depends(auth.get_current_user)):
    """Ye check karta hai ke kya user ke paas admin permissions hain."""
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access Denied: Administrative clearance required."
        )
    return current_user

# --- 3. AUTH & USER ENDPOINTS ---

@app.get("/users/me")
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": getattr(current_user, "is_admin", False)
    }

@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # First user logic: neon@admin.com hamesha admin hoga
    admin_status = True if user.email == "neon@admin.com" else False
    
    new_user = models.User(
        username=user.username, 
        email=user.email, 
        hashed_password=security.pwd_context.hash(str(user.password)), # Yahan comma zaroori hai!
        is_admin=admin_status
    )
    db.add(new_user)
    db.commit()
    return {"message": "Account created successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = security.create_access_token(data={"sub": user.email})
    return {
        "access_token": token, 
        "token_type": "bearer",
        "is_admin": user.is_admin
    }

# --- 4. DOCUMENT ENDPOINTS (Vault Management) ---

@app.post("/upload-file/")
def upload(file: UploadFile = File(...), db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    content = file.file.read()
    encrypted = security.encrypt_file(content) # AES-256 Simulation
    
    last = db.query(models.Document).filter(
        models.Document.filename == file.filename, 
        models.Document.owner_id == current_user.id
    ).order_by(models.Document.version.desc()).first()
    
    new_doc = models.Document(
        filename=file.filename, 
        content=encrypted, 
        owner_id=current_user.id, 
        version=(last.version + 1 if last else 1)
    )
    db.add(new_doc)
    
    # Log the action
    new_log = models.AuditLog(user_id=current_user.id, action=f"UPLOAD: {file.filename} (v{new_doc.version})")
    db.add(new_log)
    
    db.commit()
    return {"message": "File encrypted and saved to vault."}

@app.get("/my-documents/", response_model=List[schemas.Document])
def list_docs(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Document).filter(models.Document.owner_id == current_user.id).all()

@app.get("/download-document/{doc_id}")
def download(doc_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id, models.Document.owner_id == current_user.id).first()
    if not doc: raise HTTPException(status_code=404, detail="File not found")
    
    # Log the access
    new_log = models.AuditLog(user_id=current_user.id, action=f"DOWNLOAD: {doc.filename}")
    db.add(new_log)
    db.commit()
    
    return Response(content=security.decrypt_file(doc.content), media_type="application/octet-stream")

# --- 5. ADMIN CONTROL PANEL (User & Data Management) ---

@app.get("/admin/users/", response_model=List[schemas.User])
def get_all_users(db: Session = Depends(database.get_db), admin: models.User = Depends(check_admin)):
    """Admin sab users ki list dekh sakta hai."""
    return db.query(models.User).all()

@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db), admin: models.User = Depends(check_admin)):
    """Admin kisi bhi user ko system se remove kar sakta hai."""
    user_to_del = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_del: raise HTTPException(status_code=404, detail="User not found")
    
    # Admin khud ko delete nahi kar sakta
    if user_to_del.id == admin.id: 
        raise HTTPException(status_code=400, detail="Safety Lock: Cannot delete your own admin account.")
    
    db.delete(user_to_del)
    db.commit()
    return {"message": f"User {user_to_del.username} has been purged from system."}

@app.put("/admin/users/{user_id}/role")
def update_user_role(user_id: int, is_admin: bool, db: Session = Depends(database.get_db), admin: models.User = Depends(check_admin)):
    """Admin kisi user ke access level (Admin/User) ko change kar sakta hai."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    
    user.is_admin = is_admin
    db.commit()
    return {"message": f"User {user.username} clearance level updated to {'Admin' if is_admin else 'Standard User'}."}

@app.get("/admin/audit-logs")
def get_all_logs(db: Session = Depends(database.get_db), admin: models.User = Depends(check_admin)):
    """System mein hone wali har activity ki history."""
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).all()