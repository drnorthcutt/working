#FSND
Project 3: Catalog
==================
###40 Books Challenge App
###Author: Daniel R. Northcutt
###Date: November 2015
Overview
--------
Requirements:
Develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post images and descriptions of items.

Solution:
My project solution may have taken a slight deviation from the norm.

My wife is an Elementary/ Middle School Librarian.  During the initial phases of this project, we had a discussion that concerned a particular issue that she was having concerning the upkeep of data from a voluntary reading challenge that she uses at her school to engage students.

The 40 book challenge is essentially self describing:  it is a challenge to read 40 books during the school year.  The caveat is that these books must consist of selections from different genre, such that the challenge introduces all of these to a student in order to expand his or her awareness of them all.

This project began as a way for students to keep track of the books that he or she had read, place them into categories, and see the results of their reading somewhere other than a boring list that he or she turned in on occassion.

It evolved into a system that would allow an entire school to organize the challenge in such a way that students could view their own, others, and potentially those books from other schools that had been read.  In essence, a "goodreads" for the 40 Books Challenge.

#Contents:

[Objectives](#objectives)

[Requirements](#required-libraries-and-dependencies)

[How to](#how-to-run-this-project)

[Documentation](#documentation)

[Structure](#structure)

[Extra Credit](#extra-credit-description)
* Auth/ OAuth
* Additional API Implementation
* Image Field Usage
* CSRF Protection

[Miscellaneous](#miscellaneous)
* Application Images

#Objectives

Create a web app that demonstrates:

1.  CRUD (Create, Read, Update, Delete)
2.  JSON API endpoint implementation
3.  Third party Authentication and Authorization

May also have (for exceeds):

1.  [x] Additional API endpoint implementation
2.  [x] Image field inclusion.
3.  [x] CSRF protection.


#Required Libraries and Dependencies

[VirtualBox](https://www.virtualbox.org) (v5.0.5 used) (Must be installed separately.)

[Vagrant](https://www.vagrantup.com) (v1.7.4 used) (Must be installed separately.)

[Python v2.*](https://www.python.org)

[Flask](http://flask.pocoo.org) (v0.9 used)

[SQLAlchemy](http://www.sqlalchemy.org)

[Werkzeug](http://werkzeug.pocoo.org) (v0.8.3 used)

[oauth2client](https://github.com/google/oauth2client)

[requests](http://docs.python-requests.org/en/latest/)

[httplib2](https://github.com/jcgregorio/httplib2)

[SQLite](https://www.sqlite.org)

#How to Run this Project

Vagrant files have been provided in the Catalog Directory which should install all the necessary packages required.

Clone this repository and ensure the files are all in the same directory.
(if already cloned from the original repository, only this directory and its subdirectories are required.)

From the command line, or terminal, navigate to the Catalog folder from this repository, type:

```
vagrant up
```

ssh into the vagrant box:
```
vagrant ssh
```
Navigate to the project sync folder:
```
cd /vagrant
```

Create the databases and run the database setup files with demo content:
```
python demo_db.py
```
Success will be indicated with the message: "added school stuff!"

Run the application:
(This application runs a local web server on port 8000.  Ensure no other servers are running on port 8000.)
```
python application.py
```
From a webbrowser:
```
localhost:8000
```

It may be helpful to view a brief (if nearly 10 minutes may be called brief) YouTube demonstration of the application and its features before exploring, since there are numerous features avialable, particularly from within a login session.

[YouTube Demo](https://youtu.be/kyd9KMVF-8w)

<iframe width="420" height="315" src="https://www.youtube.com/embed/kyd9KMVF-8w" frameborder="0" allowfullscreen></iframe>

#Structure

This application utilizes numerous directories primarily for the organization and separation of publicly viewable and login viewable templates.
```
catalog
    |application files
    |configuration files
    |
    |-static
    |   |images
    |   |js files
    |   |css file
    |
    |-templates
        |main views html
        |
        |-book
        |   |new, edit, delete html
        |
        |-class
        |   |new, edit, delete html
        |   |classes view html
        |   |classroom view html
        |
        |-genre
        |   |new, edit, delete html
        |   |list view html
        |
        |-public
        |   |all public views html
        |
        |-school
        |   |new, edit, delete html
        |   |school views html
        |
        |-student
        |   |new, edit, delete html
        |   |student view html
        |
        |-teacher
            |new, edit, delete html
```


#Documentation

A brief word on in-code documentaion.  While docstrings are included in the python files, they are not (for the most part) the standard long-form, describing particular arguments, since all of the arguments in this code are self-documenting (student_id, school_id, student.email, etc).  Long segments, complex code, and exception based code is documented in-line.  HTML templates are documented for complex manipulations and/or macros.

As this project progresses, a landing page will be added for a full description of the Challenge, along with a manual for internal workings, although most are self-evident.

#Extra Credit Description
####(Images below in Miscellaneous)

Auth/OAuth (login):
* Gmail
* Google Education
* Facebook

    While numerous others are available, it seems that only these are relevent to this particular project.

API Implementation:
* JSON
* XML
* RSS/Atom feeds

    For the most part, these are available via hand typed URL Endpoints.  In the future, these will be incorporated into a Reporting System after initial testing and requests from beta participants.

Image Fields:
* Teacher Avatars (from email login)
* Student Avatars (from email login)
* Book Cover Art

    Initially, the cover art was allowed for as an upload from a client, however after conversations with numerous teachers and librarians, this functionality was removed and cover art is allowed for as a link to an image only.  This reflects the usual lack of availability of storage on school computers for images, the lower availabilty of storage on a school server were it to be installed on such a system, and allows for ease of teacher/admin editing or insertion of images should they be desired.

CSRF Protection:

A temporary token system is used on all post pages, ignoring the initial login post which uses state and a permanent session token.

 #Miscellaneous

 Images:

 Coming Soon
