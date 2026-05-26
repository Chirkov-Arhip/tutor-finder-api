from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.db.base import Base
from src.db.models.subject import tutor_subjects

class StudentProfile(Base): # наследуется от base.py
    __tablename__ = "student_profiles" # создаем таблице название

    id = Column(Integer, primary_key=True) # первичный ключ
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False) 
    # внешний ключ ссылающийся на таблицу users (колонка id), уникальный и не может быть пустым
    last_name = Column(String(50), nullable=False) # тип - строка, не может быть пустым
    first_name = Column(String(50), nullable=False) # тип - строка, не может быть пустым
    middle_name = Column(String(50)) # тип - строка
    age = Column(Integer, nullable=False) # тип - целое число, не может быть пустым
    phone = Column(String(20), nullable=False) # тип - строка, не может быть пустым
    about = Column(Text) # тип - текст (много символов)

    user = relationship("User", back_populates="student_profile") # связь один-к-одному с таблицей User
    applications = relationship("Application", back_populates="student") # связь один-ко-многим с таблицей Application


class TutorProfile(Base):
    __tablename__ = "tutor_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    age = Column(Integer, nullable=False)
    experience = Column(Integer, nullable=False)
    phone = Column(String(20), nullable=False)
    about = Column(Text)

    user = relationship("User", back_populates="tutor_profile")
    subjects = relationship("Subject", secondary=tutor_subjects, lazy="subquery")
    applications = relationship("Application", back_populates="tutor")