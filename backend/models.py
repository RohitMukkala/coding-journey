from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import Base
from datetime import datetime

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
    platform = Column(String, nullable=False)  # 'github', 'leetcode', 'codechef', 'codeforces'
    username = Column(String, nullable=False)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)

    # GitHub specific fields
    total_contributions = Column(Integer, nullable=True)
    current_streak = Column(Integer, nullable=True)
    longest_streak = Column(Integer, nullable=True)
    total_stars = Column(Integer, nullable=True)
    total_forks = Column(Integer, nullable=True)
    languages = Column(JSON, nullable=True)  # Store language percentages as JSON

    # LeetCode specific fields
    total_problems_solved = Column(Integer, nullable=True)
    easy_solved = Column(Integer, nullable=True)
    medium_solved = Column(Integer, nullable=True)
    hard_solved = Column(Integer, nullable=True)
    easy_percentage = Column(Float, nullable=True)
    medium_percentage = Column(Float, nullable=True)
    hard_percentage = Column(Float, nullable=True)

    # CodeChef specific fields
    current_rating = Column(Integer, nullable=True)
    highest_rating = Column(Integer, nullable=True)
    global_rank = Column(Integer, nullable=True)
    country_rank = Column(Integer, nullable=True)
    stars = Column(String, nullable=True)  # Changed from Integer to String to store "1★" format

    # CodeForces specific fields
    codeforces_rating = Column(Integer, nullable=True)
    codeforces_max_rating = Column(Integer, nullable=True)
    problems_solved_count = Column(Integer, nullable=True)
    contest_rating = Column(Integer, nullable=True)

    user = relationship("User", back_populates="coding_profiles")

    __table_args__ = (
        UniqueConstraint('user_id', 'platform', name='unique_user_platform'),
    )
