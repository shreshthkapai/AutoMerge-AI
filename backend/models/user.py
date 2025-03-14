from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.db import Base
from models.issue import Issue  # Added import

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_access_token = Column(String, nullable=False)

    issues = relationship("Issue", order_by=Issue.id, back_populates="user")