from sqlalchemy import Column, Integer, String
from config.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_access_token = Column(String, unique=True, nullable=False)