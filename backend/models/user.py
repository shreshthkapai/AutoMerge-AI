from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_access_token = Column(String, nullable=False)

    issues = relationship("Issue", back_populates="user")