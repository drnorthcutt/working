from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from books_setup import Admins, Schools, Base, Teachers, Classrooms, Students, Genres, Books

engine = create_engine('sqlite:///book.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
'''
A DBSession() instance establishes all conversations with the databaseand
represents a "staging zone" for all the objects loaded into the database
session object. Any change made against the objects in the session won't be
persisted into the database until you call session.commit(). If you're not
happy about the changes, you can revert all of them back to the last commit by
calling session.rollback()
'''
session = DBSession()

'''
In order to allow edits of the pre-set demo material, edit the below emails to
your own gmail or Facebook email.  You may also change the name to your own.
Your picture will automatically update on first login.  To be administrator,
change the admin email, to be a teacher, change the teacher email, or to be a
student, the student email.  The highest level email will take precedence, so
it is suggested that the student email be changed first, so that only
student edits will be available, then teacher and/or admin.
'''
#
# Demo Edit Section
#
demo_student_email = "yourEmail_1"
demo_student_name = "Johnny Q"
demo_teacher_email = "yourEmail_2"
demo_teacher_name = "Robo Teacha"
demo_admin_email = "yourEmail_3"
demo_admin_name = "Udacity Admin"


# Demo Admin
admin1 = Admins(name=demo_admin_name,
                email=demo_admin_email,
                )
session.add(admin1)
session.commit()

admin2 = Admins(name="Life Coach",
                email="something@somewhere.com",
                )
session.add(admin2)
session.commit()

# Demo school
School1 = Schools(name="Udacity",
                  state="CA",
                  district="Online",
                  admin_id=1,
                 )
session.add(School1)
session.commit()

School2 = Schools(name="Life",
                  state="CA",
                  county="Orange",
                  district="Online",
                  admin_id=2,
                 )
session.add(School2)
session.commit()

# Demo teacher
Teacher1 = Teachers(name=demo_teacher_name,
                    email=demo_teacher_email,
                    picture='http://www.ci.desoto.tx.us/images/pages/N1477/udacity%20logo.png',
                    school_id=1,
                    )
session.add(Teacher1)
session.commit()


Teacher2 = Teachers(name="Anudder Teacha",
                    email="tinnyTony@udacity.com",
                    picture='http://www.ci.desoto.tx.us/images/pages/N1477/udacity%20logo.png',
                    school_id=1,
                    )
session.add(Teacher2)
session.commit()

genre1 = Genres(teacher_id=1,
                name="Test name",
                poetry="2",
                graphic="2",
                realistic="5",
                historical="3",
                fantasy="3",
                scifi="3",
                mystery="3",
                info="7",
                bio="2",
                pages="350",
                )
session.add(genre1)
session.commit()


Classroom1 = Classrooms(grade=13,
                        teacher_id=1,
                        name="FullStack",
                        school_id=1,
                        set_id=1,
                        )
session.add(Classroom1)
session.commit()

Classroom2 = Classrooms(grade=6,
                teacher_id=1,
                name="Half-stack",
                school_id=1,
                set_id=1,
                 )
session.add(Classroom2)
session.commit()

# Demo Student
student = Students(name=demo_student_name,
                 email=demo_student_email,
                 picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png',
                 classroom=1,
                school_id=1,)

session.add(student)
session.commit()

book1 = Books(student_id=1,
              title="Great Expectations",
              author="Charles Dickens",
              image="https://upload.wikimedia.org/wikipedia/commons/8/8d/Greatexpectations_vol1.jpg",
              review="I expected more, and for it to be less sad. I almost cried when Pip tried to rip his own hair out after Estella made him cry. It's one of the saddest scenes I've ever read in my life! :(",
              genre="realistic",
              )

session.add(book1)
session.commit()

book2 = Books(student_id=1,
              title="The Book Thief",
              author="Markus Zusak",
              review="Set in Germany in the years 1939-1943, The Book Thief tells the story of Liesel, narrated by Death who has in his possession the book she wrote about these years. So, in a way, they are both book thieves.",
              genre="historical",
              )

session.add(book2)
session.commit()

book3 = Books(student_id=1,
              title="Greater Expectations",
              author="Charles Dickens",
              image="https://upload.wikimedia.org/wikipedia/commons/8/8d/Greatexpectations_vol1.jpg",
              review="I thought this was a different book.  Still made me cry... But since it could also be another category, I kept reading.",
              genre="historical",
              )

session.add(book3)
session.commit()

book4 = Books(student_id=1,
              title="The Watchmen",
              author="Alan Moore",
              image="https://upload.wikimedia.org/wikipedia/en/a/a2/Watchmen%2C_issue_1.jpg",
              review="Loved it so much I watched the movie... .",
              genre="graphic",
              )

session.add(book4)
session.commit()

book5 = Books(student_id=1,
              title="The Cat in the Hat",
              author="Dr. Seuss",
              image="https://upload.wikimedia.org/wikipedia/en/b/b5/Seuss-cat-hat.gif",
              review="Loved it so much I watched the movie...",
              genre="poetry",
              )

session.add(book5)
session.commit()

book6 = Books(student_id=1,
              title="Do Androids Dream of Elecric Sheep?",
              author="Philip K. Dick",
              review="Bladerunner!!!!!",
              genre="scifi",
              )

session.add(book6)
session.commit()

# Dummy Student
student = Students(name="Lindsey H.",
                 email="something@email.com",
                 picture='http://cdn.grid.fotosearch.com/CSP/CSP109/k1095430.jpg',
                 classroom=2,
                school_id=1,)

session.add(student)
session.commit()

book1 = Books(student_id=2,
              title="Diary of a Wimpy Kid",
              author="Jeff Kinney",
              image="http://www.wimpykid.com/wp-content/uploads/2014/03/9781419711893-350x521.jpg",
              review="Do you like books about adventure? If so,i recommend reading 'Diary of a Wimpy Kid:The long haul' by Jeff Kenney. This realistic fiction book has both comedy and adventure.I enjoyed this book because i loved all the comedy in it. I recommend this book to anybody who likes adventure,and have read the other books in this series!",
              genre="realistic"
              )

session.add(book1)
session.commit()

book2 = Books(student_id=2,
              title="Angus, thongs and full-frontal snogging : confessions of Georgia Nicolson",
              author="Rennison, Louise.",
              image="http://t1.gstatic.com/images?q=tbn:ANd9GcT58VWpXU2Lz4sFBobclA_UF_aClF2PDoQ09PebINrQUJgPj2Au",
              review="Angus thongs and full frontal snogging is a awesome book there is a lot of drama in the book. The main character in the book is Georgia she gets in trouble a lot. I think people who like drama should read this book.",
              genre="historical",
              )

session.add(book2)
session.commit()

book3 = Books(student_id=2,
              title="Rot & Ruin",
              author="Maberry, Jonathan",
              image="https://upload.wikimedia.org/wikipedia/en/f/f1/Rot_%26_Ruin_Cover.gif",
              review="This book is good for anyone who likes the ever infamous zombie apocalypse if you have ever wanted the thrill of feeling like you are there then read this book it is the best ii have read in the zombie books if you also like blood and gore read this if you dare",
              genre="scifi",
              )

session.add(book3)
session.commit()

# Dummy Student
student = Students(name="Stanley B.",
                 email="something@email.com",
                 picture='http://www.clipartbest.com/cliparts/di6/a6x/di6a6x75T.gif',
                 classroom=2,
                school_id=1,)

session.add(student)
session.commit()

book1 = Books(student_id=3,
              title="The one and only Ivan",
              author="Applegate, Katherine.",
              image="http://t1.gstatic.com/images?q=tbn:ANd9GcSxwqoXa1Y4YHFA3CZ6VWtJMkp85TankwmTbaKAjzB4yXhN5Isz",
              review="Do you want to read a book that is sad at first but turns out really happy at the end? You can go to this website to learn a lot more about Katherine Applegate books http://theoneandonlyivan.com/.  The main character is Ivan he is a gorilla and him and his other friends are facing abuse as animals in a mall/circus. The reason I love it is because it was really sad at first but turned out really happy at the end. Are you ready to read a book that is really happy at the end? Well you should.",
              genre="realistic"
              )

session.add(book1)
session.commit()

book2 = Books(student_id=3,
              title="The fourth stall",
              author="Rylander, Chris.",
              image="http://t2.gstatic.com/images?q=tbn:ANd9GcRNl6Y_f9dgi6EoXQWGeszysBIHERfDHml0US83wduLc4vFLgmu",
              review="This book tells of a teen boy that has a very helpful service.He helps out many other people and their problems.He has his own office in the abondoned fourth stall of the guys bathroom. I loved this book cause it was mysyery i love mysterys.This book is a must read.",
              genre="mystery",
              )

session.add(book2)
session.commit()

book3 = Books(student_id=3,
              title="Chomp",
              author="Hiaasen, Carl",
              image="http://ecx.images-amazon.com/images/I/41fWPq1dCdL.jpg",
              review="Want to read a book that will blow your mind? Chomp by Carl Hiaasen is the book for you. He has also written 'Scat' and 'Hoot'. The main character in the story is Wahoo Cray. His dad, Mickey is a professional animal wrangler. The two get a job offer to go somewhere in Flordia and help with the set of a Man Vs. Wild type show called 'Expedition Survival.' This book is a very, very funny and is action packed. While I was reading it I broke out laughing and frequently I was looked at as the bookworm in the class. So, if  you want read a book you will love Chomp is for you.",
              genre="realistic",
              )

session.add(book3)
session.commit()

# Dummy Student
student = Students(name="Lee H.",
                 email="something@email.com",
                 picture='http://spinoff.comicbookresources.com/wp-content/uploads/2011/05/napoleon-dynamite-thumb.jpg',
                 classroom=2,
                school_id=1,)

session.add(student)
session.commit()

book1 = Books(student_id=4,
              title="Michael Vey : the prisoner of cell 25",
              author="Evans, Richard Paul",
              image="https://upload.wikimedia.org/wikipedia/en/7/75/Michael_Vey_The_Prisoner_of_Cell_25_paperback_book_cover.jpg",
              review="The main character of the book is Michael Vey a teenager who has mysterious powers that are electric. He can shock things. He meets more people that have similar powers to his. He is also being hunted down by a company called the Elgen. I liked the book. It was one of my favorite books that I have read. It made me feel like I was in the book. It had a lot of action in it. Dangerous, daring, mysterious, and action packed, you will not want to put the book down!",
              genre="fantasy"
              )

session.add(book1)
session.commit()

# Dummy Student
student = Students(name="Claire V.",
                 email="something@email.com",
                 picture='http://images.clipartpanda.com/stick-family-decals-04_little_girl.jpg',
                 classroom=2,
                school_id=1,)

session.add(student)
session.commit()

book1 = Books(student_id=5,
              title="The Georges and the Jewels",
              author="Smiley, Jane",
              image="http://t3.gstatic.com/images?q=tbn:ANd9GcT8KFjoSKpfi0V0bS5Hlnbw8PkOivD-0WfTAg0ej7n9Ejyf24Jx",
              review="this book is set in the 1960s on a California ranch it is about a girl named Abby who helps train Tennessee walking horses and western horses. Abby finds a horse named Ornery George to be a great challenge and works hard to train the ornery horse. I liked this novel because I love horse. And I was able to connect with the mane character.  The book made me feel like if I was the one training ornery George. If you like books that make you fill like you are the mane character than this is the one.",
              genre="realistic"
              )

session.add(book1)
session.commit()



print "added school stuff!"
print "most book content courtesy of actual Elementary/ Middle School students"
