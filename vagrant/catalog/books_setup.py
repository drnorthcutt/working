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
    students = relationship("Students")
    teachers = relationship("Teachers")

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
    school = relationship("Schools")

class Genres(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key = True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    name = Column(String(80), nullable = False)
    poetry = Column(Integer)
    graphic = Column(Integer)
    realistic = Column(Integer)
    historical = Column(Integer)
    fantasy = Column(Integer)
    scifi = Column(Integer)
    mystery = Column(Integer)
    info = Column(Integer)
    bio = Column(Integer)
    pages = Column(Integer)
    teacher = relationship("Teachers", backref="genres")

class Classrooms(Base):
    __tablename__ = 'classrooms'
    id = Column(Integer, primary_key = True)
    grade = Column(Integer, nullable = False)
    name = Column(String(80))
    school_id = Column(Integer, ForeignKey('schools.id'), nullable = False)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    set_id = Column(Integer, ForeignKey('genres.id'))
    school = relationship("Schools", backref="classrooms")
    teacher = relationship("Teachers", backref="classroom")
    genres = relationship("Genres", backref="classrooms")

class Students(Base):
    __tablename__ = 'students'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))
    classroom = Column(Integer, ForeignKey('classrooms.id'))
    school_id = Column(Integer, ForeignKey('schools.id'))
    school = relationship("Schools", backref="student")
    classes = relationship("Classrooms", backref="students")


class Books(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key = True)
    student_id = Column(Integer, ForeignKey('students.id'))
    title = Column(String(250), nullable = False)
    author = Column(String(80), nullable = False)
    image = Column(String(250))
    review = Column(String(250), nullable = False)
    genre = Column(String(50), nullable = False)
    students = relationship("Students", backref="books")

engine = create_engine('sqlite:///book.db')
Base.metadata.create_all(engine)
