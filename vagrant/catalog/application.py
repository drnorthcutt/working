from flask import Flask, render_template, url_for, request, redirect, flash
from flask import jsonify
from books_setup import Schools, Teachers, Classrooms, Students, Books, Genres, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# For OAuth
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///book.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Show all schools
@app.route('/')
@app.route('/schools')
def schools():
    # return "All schools alphabetical"
    schools = session.query(Schools).order_by(Schools.name).all()
#    if 'username' not in login_session:
#        return render_template('publicschools.html',
#                               schools=schools)
#    else:
    return render_template('schools.html',
                           schools=schools)

# Show a specific school.
@app.route('/school/<int:school_id>')
def school(school_id):
    school = session.query(Schools).filter_by(id=school_id).one()
    students = (session.query(Students)
                .filter_by(school_id=school_id)
                .order_by(Students.name)
    )
    teachers = session.query(Teachers).filter_by(school_id=school_id).order_by(Teachers.name)
    books = session.query(Books).join(Students).filter(Students.school_id==school_id).all()
#    creator = getUserInfo(restaurant.user_id)
#    if 'username' not in login_session or creator.id != login_session['user_id']:
#        return render_template('publicmenu.html',
#                               items = items,
#                               restaurant = restaurant,
#                               creator = creator)
#    else:
    return render_template('school.html',
                           school = school,
                           students = students,
                           books = books,
                           teachers = teachers,
                           school_id = school_id)

# Create a new school
@app.route('/school/new', methods=['GET', 'POST'])
def newschool():
    # Check login.
#    if 'username' not in login_session:
#        return redirect('/login')
    if request.method == 'POST':
        new = Schools(name=request.form['name'],
                      state=request.form['state'],
                      county=request.form['county'],
                      district=request.form['district']
        )
        session.add(new)
        session.commit()
        flash(new.name + " created!")
        return redirect(url_for('schools'))
    else:
        return render_template('newschool.html')

# Edit a school
@app.route('/school/<int:school_id>/edit', methods=['GET', 'POST'])
def editschool(school_id):
#    if 'username' not in login_session:
#        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
#    if school.user_id != login_session['user_id']:
#        return "<script>function myFunction() {alert('You are not authorized to edit this school.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            school.name = request.form['name']
        if request.form['state']:
            school.state = request.form['state']
        if request.form['county']:
            school.county = request.form['county']
        if request.form['district']:
            school.district = request.form['district']
        session.add(school)
        session.commit()
        flash(school.name + " edited!")
        return redirect(url_for('schoolstudents', school_id = school_id))
    else:
        return render_template('editschool.html',
                               school_id=school_id,
                               school=school)

# Delete a school
@app.route('/school/<int:school_id>/delete', methods=['GET', 'POST'])
def deleteschool(school_id):
#    if 'username' not in login_session:
#        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
#    if school.user_id != login_session['user_id']:
#        return "<script>function myFunction() {alert('You are not authorized to delete this restaurant.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(school)
        session.commit()
        flash(school.name + " deleted!")
        return redirect(url_for('schools'))
    else:
        return render_template('deleteschool.html',
                               school = school,
                               school_id = school_id)

# Show a specific school's teachers
@app.route('/school/<int:school_id>/teachers')
def schoolteachers(school_id):
    school = session.query(Schools).filter_by(id=school_id).one()
    teachers = session.query(Teachers).filter_by(school_id=school_id)
#    creator = getUserInfo(restaurant.user_id)
#    if 'username' not in login_session or creator.id != login_session['user_id']:
#        return render_template('publicmenu.html',
#                               items = items,
#                               restaurant = restaurant,
#                               creator = creator)
#    else:
    return render_template('teachers.html',
                           school = school,
                           teachers = teachers,
                           school_id = school_id)

# Add a teacher.
@app.route('/school/<int:school_id>/teacher/new', methods=['GET', 'POST'])
def newteacher(school_id):
    school = session.query(Schools).filter_by(id=school_id).one()
    if request.method == 'POST':
        new = Teachers(name=request.form['name'],
                       email=request.form['email'],
                       picture=request.form['picture'],
                       school_id=school_id
        )
        session.add(new)
        session.commit()
        flash(new.name + " added!")
        return redirect(url_for('schoolteachers', school_id=school_id))
    else:
        return render_template('newteacher.html',
                               school_id=school_id,
                               school=school)

# Edit a teacher.
@app.route('/school/<int:school_id>/teacher/<int:teacher_id>/edit',
           methods=['GET', 'POST'])
def editteacher(school_id, teacher_id):
    school = session.query(Schools).filter_by(id=school_id).one()
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    if request.method == 'POST':
        if request.form['name']:
            teacher.name = request.form['name']
        if request.form['email']:
            teacher.email = request.form['email']
        if request.form['picture']:
            teacher.picture = request.form['picture']
        session.add(teacher)
        session.commit()
        flash(teacher.name + " edited!")
        return redirect(url_for('schoolteachers', school_id=school_id))
    else:
        return render_template('editteacher.html',
                               school_id = school_id,
                               teacher_id = teacher_id,
                               teacher = teacher,
                               school = school)

# Delete a teacher.
@app.route('/school/<int:school_id>/teacher/<int:teacher_id>/delete',
           methods=['GET', 'POST'])
def deleteteacher(school_id, teacher_id):
#    if 'username' not in login_session:
#        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
#    if school.user_id != login_session['user_id']:
#        return "<script>function myFunction() {alert('You are not authorized to delete this restaurant.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(teacher)
        session.commit()
        flash(teacher.name + " deleted!")
        return redirect(url_for('schoolteachers', school_id = school_id))
    else:
        return render_template('deleteteacher.html',
                               school = school,
                               teacher = teacher,
                               teacher_id = teacher_id,
                               school_id = school_id)

# Show a teacher's classroom(s).
@app.route('/teacher/<int:teacher_id>/classroom')
def classroom(teacher_id):
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    classroom = session.query(Classrooms).filter_by(teacher_id=teacher_id)
    students = (session.query(Students)
                .filter(Students.classroom == Classrooms.id)
                .filter(Classrooms.teacher_id == teacher_id)
                .order_by(Students.name))
    noclass = (session.query(Students)
               .filter(Students.classroom == '0')
               .filter(Students.school_id == teacher.school_id)
               .order_by(Students.name).all())
    books = (session.query(Books)
             .join(Students)
             .join(Classrooms)
             .filter_by(teacher_id=teacher_id).all())
#    creator = getUserInfo(restaurant.user_id)
#    if 'username' not in login_session or creator.id != login_session['user_id']:
#        return render_template('publicmenu.html',
#                               items = items,
#                               restaurant = restaurant,
#                               creator = creator)
#    else:
    print books
    return render_template('classes.html',
                           teacher = teacher,
                           students = students,
                           classroom = classroom,
                           noclass = noclass,
                           books = books,
                           teacher_id = teacher_id)

# Show a specific room (for cases when more than one exist for a teacher).
@app.route('/teacher/<int:teacher_id>/classroom/<int:room_id>')
def room(teacher_id, room_id):
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    classroom = session.query(Classrooms).filter_by(id=room_id).one()
    classother = session.query(Classrooms).filter_by(teacher_id=teacher_id)
    students = (session.query(Students)
                .filter(Students.classroom == Classrooms.id)
                .filter(Classrooms.teacher_id == teacher_id)
                .order_by(Students.name))
    students = (session.query(Students)
                .filter(Students.classroom==room_id)
                .order_by(Students.name))
    books = (session.query(Books)
             .join(Students)
             .filter(Students.classroom==room_id).all())
#    creator = getUserInfo(restaurant.user_id)
#    if 'username' not in login_session or creator.id != login_session['user_id']:
#        return render_template('publicmenu.html',
#                               items = items,
#                               restaurant = restaurant,
#                               creator = creator)
#    else:
    return render_template('classroom.html',
                           teacher = teacher,
                           students = students,
                           books = books,
                           classroom = classroom,
                           classother = classother,
                           teacher_id = teacher_id,
                           room_id = room_id)

# Add a classroom by teacher.
@app.route('/teacher/<int:teacher_id>/classroom/new', methods=['GET', 'POST'])
def newclass(teacher_id):
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    classes = (session.query(Classrooms)
              .filter_by(teacher_id=teacher_id)
              .order_by(Classrooms.grade, Classrooms.name))
    sets = session.query(Genres).filter_by(teacher_id=teacher_id).all()
    if request.method == 'POST':
        new = Classrooms(name=request.form['name'],
                         grade=request.form['grade'],
                         set_id=request.form['set'],
                         teacher_id=teacher_id,
                         school_id=teacher.school_id
                        )
        session.add(new)
        session.commit()
        flash(new.name + " added!")
        return redirect(url_for('classroom', teacher_id=teacher_id))
    else:
        return render_template('newclass.html',
                               teacher = teacher,
                               classes = classes,
                               sets = sets,
                               teacher_id = teacher_id)

# Edit a teacher.
@app.route('/teacher/<int:teacher_id>/classroom/<int:class_id>/edit',
           methods=['GET', 'POST'])
def editclass(teacher_id, class_id):
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    grades = (session.query(Classrooms)
              .filter_by(teacher_id=teacher_id)
              .order_by(Classrooms.grade, Classrooms.name))
    allteach = session.query(Teachers).filter_by(school_id=teacher.school_id)
    classroom = session.query(Classrooms).filter_by(id=class_id).one()
    sets = session.query(Genres).filter_by(teacher_id=teacher_id).all()
    if request.method == 'POST':
        if request.form['name']:
            classroom.name = request.form['name']
        if request.form['grade']:
            classroom.grade = request.form['grade']
        if request.form['set']:
            classroom.set_id = request.form['set']
        if request.form['teacher']:
            classroom.teacher_id = request.form['teacher']
        session.add(classroom)
        session.commit()
        flash(classroom.name + " edited!")
        return redirect(url_for('classroom', teacher_id=teacher_id))
    else:
        return render_template('editclass.html',
                               teacher = teacher,
                               grades = grades,
                               classroom = classroom,
                               allteach = allteach,
                               teacher_id = teacher_id,
                               class_id = class_id)

# Delete a classroom.
@app.route('/teacher/<int:teacher_id>/classroom/<int:class_id>/delete', methods=['GET', 'POST'])
def deleteclass(teacher_id, class_id):
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    classroom = session.query(Classrooms).filter_by(id=class_id).one()
    if request.method == 'POST':
        session.delete(classroom)
        session.commit()
        flash(classroom.name + " deleted!")
        return redirect(url_for('classroom', teacher_id = teacher_id))
    else:
        return render_template('deleteclass.html',
                               teacher = teacher,
                               classroom = classroom,
                               teacher_id = teacher_id,
                               class_id = class_id)


# Show a specific school's students.
@app.route('/school/<int:school_id>/students')
def schoolstudents(school_id):
    school = session.query(Schools).filter_by(id=school_id).one()
    grades = (session.query(Students)
                .filter_by(school_id=school_id)
                .order_by(Students.name)
                .all())
    students = session.query(Students).filter_by(school_id=school_id).all()
    tests = session.query(Classrooms).outerjoin(Students).filter_by(school_id=school_id).all()
#    creator = getUserInfo(restaurant.user_id)
#    if 'username' not in login_session or creator.id != login_session['user_id']:
#        return render_template('publicmenu.html',
#                               items = items,
#                               restaurant = restaurant,
#                               creator = creator)
#    else:
    print grades
    for student in students:
        print student
    return render_template('students.html',
                           school = school,
                           students = students,
                           grades = grades,
                           tests = tests,
                           school_id = school_id)

# Add a student.
@app.route('/school/<int:school_id>/student/new', methods=['GET', 'POST'])
def newstudent(school_id):
    school = session.query(Schools).filter_by(id=school_id).one()
    teachers = session.query(Teachers).filter_by(school_id=school_id).all()
    classes = session.query(Classrooms).filter_by(school_id=school_id)
    if request.method == 'POST':
        new = Students(name=request.form['name'],
                    email=request.form['email'],
                    picture=request.form['picture'],
                    classroom=request.form['classroom'],
                    school_id=school_id
                    )
        session.add(new)
        session.commit()
        flash(new.name + " added!")
        return redirect(url_for('schoolstudents', school_id=school_id))
    else:
        return render_template('newstudent.html',
                               school_id=school_id,
                               classes = classes,
                               school=school)

# Edit a student.
@app.route('/school/<int:school_id>/student/<int:user_id>/edit', methods=['GET', 'POST'])
def editstudent(school_id, user_id):
    school = session.query(Schools).filter_by(id=school_id).one()
    teachers = session.query(Teachers).filter_by(school_id=school_id).all()
    classes = session.query(Classrooms).filter_by(school_id=school_id)
    student = session.query(Students).filter_by(id=user_id).one()
    if request.method == 'POST':
        if request.form['name']:
            student.name = request.form['name']
        if request.form['email']:
            student.email = request.form['email']
        if request.form['picture']:
            student.picture = request.form['picture']
        if request.form['classroom']:
            student.classroom = request.form['classroom']
        session.add(student)
        session.commit()
        flash(student.name + " edited!")
        return redirect(url_for('schoolstudents', school_id=school_id))
    else:
        return render_template('editstudent.html',
                               school_id = school_id,
                               user_id = user_id,
                               student = student,
                               classes = classes,
                               teachers = teachers,
                               school = school)

# Delete a student
@app.route('/school/<int:school_id>/student/<int:user_id>/delete', methods=['GET', 'POST'])
def deletestudent(school_id, user_id):
#    if 'username' not in login_session:
#        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    student = session.query(Students).filter_by(id=user_id).one()
#    if school.user_id != login_session['user_id']:
#        return "<script>function myFunction() {alert('You are not authorized to delete this restaurant.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(student)
        session.commit()
        flash(student.name + " deleted!")
        return redirect(url_for('schoolstudents', school_id = school_id))
    else:
        return render_template('deletestudent.html',
                               school = school,
                               student = student,
                               user_id = user_id,
                               school_id = school_id)

# Show a student's books.
@app.route('/<int:teacher_id>/student/<int:student_id>')
def student(student_id, teacher_id):
    student = session.query(Students).filter_by(id=student_id).one()
    genre = session.query(Genres).join(Classrooms).filter_by(teacher_id=teacher_id)
    books = session.query(Books).filter_by(student_id=student_id)
#    creator = getUserInfo(restaurant.user_id)
#    if 'username' not in login_session or creator.id != login_session['user_id']:
#        return render_template('publicmenu.html',
#                               items = items,
#                               restaurant = restaurant,
#                               creator = creator)
#    else:
    return render_template('student.html',
                           student = student,
                           books = books,
                           genre = genre,
                           student_id = student_id,
                           teacher_id = teacher_id)

# Add a student book.
@app.route('/student/<int:student_id>/book/add', methods=['GET', 'POST'])
def newbook(student_id):
    student = session.query(Students).filter_by(id=student_id).one()
    if request.method == 'POST':
        new = Books(title = request.form['title'],
                    author = request.form['author'],
                    image = request.form['image'],
                    review = request.form['review'],
                    genre = request.form['genre'],
                    student_id = student_id
                    )
        session.add(new)
        session.commit()
        flash(new.title + " added!")
        return redirect(url_for('student', student_id=student.id, teacher_id=student.classes.teacher_id))
    else:
        return render_template('newbook.html',
                               student_id = student_id,
                               student = student)

# Edit a student book
@app.route('/student/<int:student_id>/book/<int:book_id>/edit', methods=['GET', 'POST'])
def editbook(student_id, book_id):
    student = session.query(Students).filter_by(id=student_id).one()
    book = session.query(Books).filter_by(id=book_id).one()
    if request.method == 'POST':
        if request.form['title']:
            book.title = request.form['title']
        if request.form['author']:
            book.author = request.form['author']
        if request.form['image']:
            book.image = request.form['image']
        if request.form['review']:
            book.review = request.form['review']
        if request.form['genre']:
            book.genre = request.form['genre']
        book.user_id = student_id
        session.add(book)
        session.commit()
        flash(book.title + " edited!")
        return redirect(url_for('student', student_id=student.id, teacher_id=student.classes.teacher_id))
    else:
        return render_template('editbook.html',
                               student_id = student_id,
                               book_id = book_id,
                               student = student,
                               book = book)

# Delete a student book.
@app.route('/student/<int:student_id>/book/<int:book_id>/delete', methods=['GET', 'POST'])
def deletebook(student_id, book_id):
#    if 'username' not in login_session:
#        return redirect('/login')
    book = session.query(Books).filter_by(id=book_id).one()
    student = session.query(Students).filter_by(id=student_id).one()
#    if school.user_id != login_session['user_id']:
#        return "<script>function myFunction() {alert('You are not authorized to delete this restaurant.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(book)
        session.commit()
        flash(book.title + " deleted!")
        return redirect(url_for('student',
                                student_id = student.id,
                                teacher_id = student.classes.teacher_id))
    else:
        return render_template('deletebook.html',
                               student = student,
                               student_id = student_id,
                               book = book,
                               book_id = book_id)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
