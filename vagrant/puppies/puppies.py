from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Shelter(Base):
    __tablename__ = 'shelter'
    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    address = Column(String(250))
    city = Column(String(80))
    state = Column(String(20))
    zipCode = Column(String(10))
    website = Column(String)
    capacity = Column(Integer)
    inmates = Column(Integer)


class Puppy(Base):
    __tablename__ = 'puppy'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    gender = Column(String(6), nullable = False)
    dateOfBirth = Column(Date)
    picture = Column(String)
    pid = Column(Integer, ForeignKey('profile.id'))
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
    shelter = relationship(Shelter)
    weight = Column(Numeric(10))
#    adopter = relationship("Adopters",
#                    secondary=adoption_table,
#                    backref="puppy")

class Profile(Base):
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    needs = Column(String(250))
    description = Column(String(250))
    puppy = relationship(Puppy)

class Adopters(Base):
    __tablename__ = 'adopters'
    id = Column(Integer, primary_key=True)
    name = Column(String(80))

#adoption_table = Table('adoption', Base.metadata,
#    Column('puppy', Integer, ForeignKey('puppy.id')),
 #   Column('adopters', Integer, ForeignKey('adopters.id'))


# engine = create_engine('sqlite:///puppyshelter.db')


# Base.metadata.create_all(engine)
