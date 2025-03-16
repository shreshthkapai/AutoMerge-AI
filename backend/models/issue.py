from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from config.db import Base

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    github_issue_id = Column(Integer, unique=True, index=True)
    title = Column(String, nullable=False)
    repo_full_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    state = Column(String, default="open")
    html_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_ai_fixable = Column(Boolean, default=False)
    labels = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="issues")
    fixes = relationship("Fix", back_populates="issue")