from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from database import Base


# AGENT: write your SQLAlchemy model classes here
#
# Rules:
# 1. Every model inherits from Base
# 2. Every model has: id = Column(Integer, primary_key=True, index=True)
# 3. Use __tablename__ to set the table name (lowercase plural recommended)
# 4. Do NOT add new imports — everything you need is already imported above
#
# Example shape:
#
# class Todo(Base):
#     __tablename__ = "todos"
#     id          = Column(Integer, primary_key=True, index=True)
#     title       = Column(String, nullable=False)
#     completed   = Column(Boolean, default=False)
#     created_at  = Column(DateTime)
