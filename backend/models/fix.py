from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import  relationship
from datetime import datetime
from config.db import Base

class Fix(Base):
    __tablename__ = "fixes"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    content = Column(Text, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_submitted = Column(Boolean, default=False)
    submission_message = Column(String, nullable=True)
    pr_url = Column(String, nullable=True)

    issue = relationship("Issue", back_populates="fixes")