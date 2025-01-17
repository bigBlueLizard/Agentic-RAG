from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    sign_up_date = Column(DateTime, nullable=False)
    pfp = Column(String, nullable=False)
    
    queries = relationship("Query", back_populates="user")


class Query(Base):
    __tablename__ = 'query'
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    user = relationship("User", back_populates="queries")


engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)
