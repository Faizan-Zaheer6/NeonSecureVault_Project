from sqlalchemy import Column, Integer, Boolean, String, LargeBinary, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)

    # Relationships: Aik user ki bohot si files aur logs ho sakte hain
    documents = relationship("Document", back_populates="owner")
    logs = relationship("AuditLog", back_populates="user")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    content = Column(LargeBinary)
    upload_date = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1) 
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationship: File ka aik hi owner hota hai
    owner = relationship("User", back_populates="documents")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String) # Example: "Login", "File Uploaded", "Downloaded"
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship back to User
    user = relationship("User", back_populates="logs")