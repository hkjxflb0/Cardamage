from sqlalchemy.ext.declarative import declarative_base

from components.database import get_db
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

db = get_db()
Base = declarative_base()


class Content(Base):
    __tablename__ = "content"
   
    id = Column(Integer, primary_key=True, index=True)
    video_url = Column(String, nullable=False)
    flag = Column(String, nullable=False)
    raider_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
   
    class Config:
        orm_mode = True