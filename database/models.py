from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy.orm import declarative_base,relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


Base = declarative_base()



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    downloads = relationship("Download", back_populates="user")


class Download(Base):
    __tablename__ = 'downloads'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    link = Column(String, index=True)
    quality = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="downloads")
