from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from books_setup import Schools, Base, Teachers, Grades, Users, Genres, Books

engine = create_engine('sqlite:///book.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy school
School1 = Schools(name="Udacity",
                  state="CA",
                  district="Online",
                 )
session.add(School1)
session.commit()

# Create dummy user
Teacher1 = Teachers(name="Robo Teacha",
                 email="tinnyTim@udacity.com",
                 picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png',
                 )
session.add(Teacher1)
session.commit()

Grade1 = Grades(num="13",
                teacher_id=1,
                 )
session.add(Grade1)
session.commit()

genre1 = Genres(grade_id=1,
                poetry="2",
                graphic="2",
                realistic="5",
                historical="3",
                fantasy="3",
                scifi="3",
                mystery="3",
                info="7",
                bio="2",
                choice="10",
                pages="350",
                )
session.add(genre1)
session.commit()


# Dummy Student
student1 = Users(name="Johnny Q",
                 email="something@email.com",
                 picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png',
                 grade="13",
                 teacher_id=1,)

session.add(student1)
session.commit()

book1 = Books(users=student1,
              title="Great Expectations",
              author="Charles Dickens",
              image="https://upload.wikimedia.org/wikipedia/commons/8/8d/Greatexpectations_vol1.jpg",
              review="I expected more, and for it to be less sad. I almost cried when Pip tried to rip his own hair out after Estella made him cry. It's one of the saddest scenes I've ever read in my life! :(",
              genre="realistic",
              )

session.add(book1)
session.commit()

book2 = Books(users=student1,
              title="The Book Thief",
              author="Markus Zusak",
              review="Set in Germany in the years 1939-1943, The Book Thief tells the story of Liesel, narrated by Death who has in his possession the book she wrote about these years. So, in a way, they are both book thieves.",
              genre="historical",
              )

session.add(book2)
session.commit()


print "added menu items!"
