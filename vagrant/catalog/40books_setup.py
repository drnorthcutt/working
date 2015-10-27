import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Teachers(Base):
    __tablename__ = 'teachers'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))

class Grades(Base):
    __tablename__ = 'grades'
    id = Column(Integer, primary_key = True)
    num = Column(Integer, nullable = False)
    teacher_id = (Integer, ForeignKey('teachers.id'))
    teachers = relationship(Teachers)

class Schools(Base):
    __tablename__ = 'schools'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    state = Column(String(2), nullable = False)
    county = Column(String(80))
    district = Column(String(80))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    teachers = relationship(Teachers)

    @property
    def serialize(self):
        # Return data serializeable
        return {
            'id' : self.id,
            'name' : self.name,
            'state': self.state,
        }

class Users(Base):
    __tablename__ = 'users'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))
    grade = Column(Integer, nullable = False)
    school_id = Column(Integer, ForeignKey('schools.id'))
    teacher = Column(Integer, ForeignKey('teachers.id'))
    schools = relationship(Schools)
    teachers = relationship(Teachers)

class Genres(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key = True)
    grade_id = Column(Integer, ForeignKey('grades.id'))
    poetry = Column(Integer)
    graphic = Column(Integer)
    realistic = Column(Integer)
    historical = Column(Integer)
    fantasy = Column(Integer)
    scifi = Column(Integer)
    mystery = Column(Integer)
    info = Column(Integer)
    bio = Column(Integer)
    choice = Column(Integer)
    pages = Column(Integer)
    grades = relationship(Grades)

class Genres(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(250), nullable = False)
    author = Column(String(80), nullable = False)
    image = Column(String(250))
    review = Column(String(250), nullable = False)
    genre = Column(String(50), nullable = False)
    users = relationship(Users)

engine = create_engine('sqlite:///40books.db')
Base.metadata.create_all(engine)
