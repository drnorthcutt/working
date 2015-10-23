from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from puppies import Base, Shelter, Puppy, Profile, Adopters
import datetime

engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def GetAllPuppies():
    """Print all puppy names alphabetically."""
    res = session.query(Puppy).order_by(Puppy.name).all()
    print "\nPuppy Name and Shelter Id\n"
    for puppy in res:
        print puppy.name, puppy.shelter_id

def GetPuppiesAge():
    """Print puppies less than 6 months old."""
    today = datetime.date.today()
    days_old = 183
    six_months = today - datetime.timedelta(days = days_old)
    res = (session.query(Puppy).filter(Puppy.dateOfBirth > six_months)
           .order_by("dateOfBirth desc"))
    print "\nPuppy Name and DOB\n"
    for puppy in res:
        print puppy.name, puppy.dateOfBirth

def GetPuppiesWeight():
    """Print puppies and weight."""
    res = session.query(Puppy).order_by(Puppy.weight).all()
    print "\nPuppy Name and Weight\n"
    for puppy in res:
        print puppy.name, puppy.weight

# Print puppies grouped by shelter
def GetPuppiesShelter():
    """Print puppies grouped by shelter."""
    res = session.query(Puppy).order_by(Puppy.shelter_id).all()
    print "\nPuppy Name and Shelter\n"
    for puppy in res:
        print puppy.name, puppy.shelter.name

def GetShelterCapacity(shelter_id):
    res = session.query(Puppy, Shelter).filter(Shelter.id == shelter_id).all()
#    print "\nShelter Capacity\n"
#    for shelter in res:
#        available = (Shelter.capacity - inmates)
#        print Shelter.name, available

def GetShelterInmates(shelter_id):
    return (session.query(Puppy, Shelter).join(Shelter)
           .filter(Shelter.id == shelter_id).count())


def PuppyToShelter(puppy_name, puppy_weight, shelter_id):
	if (GetShelterInmates(shelter_id) >= GetShelterCapacity(shelter_id)):
		home = session.query(Puppy).filter(Puppy.id == puppy_id).one()
		home.shelter_id = shelter_id
		session.add(home)
		session.commit()
		print "Puppy added to shelter."
		return None
	nohome = session.query(Puppy).filter(Puppy.id == puppy_id).one()
	print '%s has been put to sleep. There was no room in the shelter.' % nohome.name
	session.delete(nohome)
	session.commit()
	return None

if __name__ == '__main__':
  while 1:
    print("""
    1) For all puppy names in alphabetical order.
    2) For 6 months and under with names and DOB.
    3) For weights.
    4) For puppies by shelter
    5) For Shelters and capacity
    6) Exit.
    """)
    selection = int(input('Select: '))
    if selection == 1:
        GetAllPuppies()
    elif selection == 2:
        GetPuppiesAge()
    elif selection == 3:
        GetPuppiesWeight()
    elif selection == 4:
        GetPuppiesShelter()
    elif selection == 5:
        GetShelterCapacity(1)
    elif selection == 6:
        print PuppyToShelter('Jessica',2.34,1)
        print GetShelterInmates(1)
        print GetShelterInmates(2)
        print GetShelterInmates(3)
        print GetShelterInmates(4)
        print GetShelterInmates(5)
#        print adoptPuppies(11,[1])
#        print getShelterOccupancy(1)
#        print getShelterOccupancy(2)
#        print getShelterOccupancy(3)
#        print getShelterOccupancy(4)
#        print getShelterOccupancy(5)
    elif selection == 7:
        exit()





