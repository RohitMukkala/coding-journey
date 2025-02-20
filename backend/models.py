from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)  # Hashed password
    profile_picture = Column(String, nullable=True)  # URL to profile picture
    leetcode_username = Column(String, nullable=True)
    github_username = Column(String, nullable=True)
    codechef_username = Column(String, nullable=True)
    codeforces_username = Column(String, nullable=True)

    coding_profiles = relationship("CodingProfile", back_populates="user", cascade="all, delete-orphan")

class CodingProfile(Base):
    __tablename__ = "coding_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String, nullable=False)
    profile_link = Column(String, nullable=True)
    rating = Column(Integer, nullable=True)

    user = relationship("User", back_populates="coding_profiles")
