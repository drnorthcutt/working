import os
import sys
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Schools(Base):
    __tablename__ = 'schools'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    admin_id = Column(Integer, ForeignKey('admins.id'))
    state = Column(String(2), nullable = False)
    county = Column(String(80))
    district = Column(String(80))
    students = relationship("Students")
    teachers = relationship("Teachers")
    admin = relationship("Admins")

    @property
    def serialize(self):
        # Return data serializeable
        return {
            'ID' : self.id,
            'name' : self.name,
            'State' : self.state,
            'County' : self.county,
            'District' : self.district,
        }


class Admins(Base):
    __tablename__ = 'admins'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key =True)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))
    school = relationship("Schools", backref="admins")


class Teachers(Base):
    __tablename__ = 'teachers'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))
    school_id = Column(Integer, ForeignKey('schools.id'))
    school = relationship("Schools")
    classes = relationship("Classrooms")

    @property
    def serialize(self):
        # Return data serializeable
        return {
            'ID' : self.id,
            'name' : self.name,
        }


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
    studs = relationship("Students")

    @property
    def serialize(self):
        # Return data serializeable
        return {
            'ID' : self.id,
            'Grade' : self.grade,
            'Name' : self.name,
            'Teacher' : self.teacher.name,
            'Genre List' : self.genres.name,
        }


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
    book = relationship("Books")

    # Except in case a student has not been placed in a class
    @property
    def serialize(self):
        # Return data serializeable
        try:
            return {
                'ID' : self.id,
                'name' : self.name,
                'Grade' : self.classes.grade,
                'Class Name' : self.classes.name,
            }
        except:
            return {
                'ID' : self.id,
                'name' : self.name,
            }


class Books(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key = True)
    student_id = Column(Integer, ForeignKey('students.id'))
    title = Column(String(250), nullable = False)
    author = Column(String(80), nullable = False)
    image = Column(String(250))
    review = Column(String(250), nullable = False)
    genre = Column(String(50), nullable = False)
    date = Column(DateTime, default=datetime.utcnow)
    students = relationship("Students", backref="books")

    @property
    def serialize(self):
        # Return data serializeable
        return {
            'ID' : self.id,
            'Genre' : self.genre,
            'Title' : self.title,
            'Author' : self.author,
            'Review' : self.review,
            'Student' : self.students.name,
            'Student ID' : self.students.id,
        }


engine = create_engine('sqlite:///book.db')
Base.metadata.create_all(engine)
