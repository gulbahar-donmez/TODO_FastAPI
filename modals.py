from database import Base
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey


class Todos(Base):
    __tablename__ = "todoo"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    des = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))  # Düzeltildi


class Users(Base):
    __tablename__ = "users"  # Düzeltildi

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String)  # Düzeltildi
    first_name = Column(String)  # Düzeltildi
    last_name = Column(String)  # Düzeltildi
    hashed_password = Column(String)  # Daha anlamlı isim
    is_active = Column(Boolean, default=True)  # Düzeltildi
    role = Column(String)
