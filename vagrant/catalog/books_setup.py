import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Schools(Base):
    __tablename__ = 'schools'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    state = Column(String(2), nullable = False)
    county = Column(String(80))
    district = Column(String(80))

    @property
    def serialize(self):
        # Return data serializeable
        return {
            'id' : self.id,
            'name' : self.name,
            'state': self.state,
        }

class Teachers(Base):
    __tablename__ = 'teachers'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))
    school_id = Column(Integer, ForeignKey('schools.id'))
    schools = relationship(Schools)

class Grades(Base):
    __tablename__ = 'grades'
    id = Column(Integer, primary_key = True)
    num = Column(Integer, nullable = False)
    name = Column(String(80))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    teachers = relationship(Teachers)

class Users(Base):
    __tablename__ = 'users'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))
    grade = Column(Integer, nullable = False)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    school_id = Column(Integer, ForeignKey('schools.id'))
    teachers = relationship(Teachers)
    schools = relationship(Schools)

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

class Books(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(250), nullable = False)
    author = Column(String(80), nullable = False)
    image = Column(String(250))
    review = Column(String(250), nullable = False)
    genre = Column(String(50), nullable = False)
    users = relationship(Users)

engine = create_engine('sqlite:///book.db')
Base.metadata.create_all(engine)
