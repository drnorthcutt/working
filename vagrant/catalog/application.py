from flask import Flask, render_template, url_for, request, redirect, flash
from flask import jsonify
from books_setup import Schools, Teachers, Grades, Users, Genres, Books, Base
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
                           num = num,
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
@app.route('/school/<int:school_id>/teacher/<int:teacher_id>/edit', methods=['GET', 'POST'])
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
@app.route('/school/<int:school_id>/teacher/<int:teacher_id>/delete', methods=['GET', 'POST'])
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

# Show a specific classroom.
@app.route('/class/<int:teacher_id>/classroom')
def classroom(teacher_id):
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    students = (session.query(Users)
                .filter_by(teacher_id=teacher_id)
                .order_by(Users.name)
                .all())
#    creator = getUserInfo(restaurant.user_id)
#    if 'username' not in login_session or creator.id != login_session['user_id']:
#        return render_template('publicmenu.html',
#                               items = items,
#                               restaurant = restaurant,
#                               creator = creator)
#    else:
    print students
    print teacher
    return render_template('classes.html',
                           teacher = teacher,
                           students = students,
                           teacher_id = teacher_id)

# Add a classroom.
@app.route('/teacher/<int:teacher_id>/classroom/new', methods=['GET', 'POST'])
def newclass(teacher_id):
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    grades = (session.query(Grades)
              .filter_by(teacher_id=teacher_id)
              .order_by(num, name))
    if request.method == 'POST':
        new = Grades(name=request.form['name'],
                    num=request.form['grade'],
                    teacher_id=teacher_id
                    )
        session.add(new)
        session.commit()
        flash(new.num +  new.name + " added!")
        return redirect(url_for('classroom', teacher_id=teacher_id))
    else:
        return render_template('newclass.html',
                               teacher = teacher,
                               grades = grades,
                               teacher_id = teacher_id)

# Edit a teacher.
@app.route('/teacher/<int:teacher_id>/classroom/<int:class_id>/edit', methods=['GET', 'POST'])
def editclass(teacher_id, class_id):
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    grades = (session.query(Grades)
              .filter_by(teacher_id=teacher_id)
              .order_by(num, name))
    allteach = session.query(Teachers).filter_by(school_id=teacher.school_id)
    classroom = session.query(Grades).filter_by(class_id).one()
    if request.method == 'POST':
        if request.form['name']:
            classroom.name = request.form['name']
        if request.form['grade']:
            classroom.num = request.form['grade']
        if request.form['teacher']:
            classroom.teacher_id = request.form['teacher']
        session.add(teacher)
        session.commit()
        flash(new.num +  new.name + " edited!")
        return redirect(url_for('classroom', teacher_id=teacher_id))
    else:
        return render_template('editclass.html',
                               teacher = teacher,
                               grades = grades,
                               classroom = classroom,
                               allteach = allteach,
                               teacher_id = teacher_id,
                               class_id = class_id)

# Show a specific school's students.
@app.route('/school/<int:school_id>/students')
def schoolstudents(school_id):
    school = session.query(Schools).filter_by(id=school_id).one()
    students = (session.query(Users)
                .filter_by(school_id=school_id)
                .order_by(Users.name)
                .all())
#    creator = getUserInfo(restaurant.user_id)
#    if 'username' not in login_session or creator.id != login_session['user_id']:
#        return render_template('publicmenu.html',
#                               items = items,
#                               restaurant = restaurant,
#                               creator = creator)
#    else:
    return render_template('students.html',
                           school = school,
                           students = students,
                           school_id = school_id)

# Add a student.
@app.route('/school/<int:school_id>/student/new', methods=['GET', 'POST'])
def newstudent(school_id):
    school = session.query(Schools).filter_by(id=school_id).one()
    teachers = session.query(Teachers).filter_by(school_id=school_id).all()
    if request.method == 'POST':
        new = Users(name=request.form['name'],
                    email=request.form['email'],
                    picture=request.form['picture'],
                    grade=request.form['grade'],
                    teacher_id=request.form['teacher'],
                    school_id=school_id
                    )
        session.add(new)
        session.commit()
        flash(new.name + " added!")
        return redirect(url_for('schoolstudents', school_id=school_id))
    else:
        return render_template('newstudent.html',
                               school_id=school_id,
                               teachers = teachers,
                               school=school)

# Edit a student.
@app.route('/school/<int:school_id>/student/<int:user_id>/edit', methods=['GET', 'POST'])
def editstudent(school_id, user_id):
    school = session.query(Schools).filter_by(id=school_id).one()
    teachers = session.query(Teachers).filter_by(school_id=school_id).all()
    student = session.query(Users).filter_by(id=user_id).one()
    if request.method == 'POST':
        if request.form['name']:
            student.name = request.form['name']
        if request.form['email']:
            student.email = request.form['email']
        if request.form['picture']:
            student.picture = request.form['picture']
        if request.form['grade']:
            student.grade = request.form['grade']
        if request.form['teacher']:
            student.teacher_id = request.form['teacher']
        session.add(student)
        session.commit()
        flash(student.name + " edited!")
        return redirect(url_for('schoolstudents', school_id=school_id))
    else:
        return render_template('editstudent.html',
                               school_id = school_id,
                               user_id = user_id,
                               student = student,
                               teachers = teachers,
                               school = school)

# Delete a student
@app.route('/school/<int:school_id>/student/<int:user_id>/delete', methods=['GET', 'POST'])
def deletestudent(school_id, user_id):
#    if 'username' not in login_session:
#        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    student = session.query(Users).filter_by(id=user_id).one()
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
    student = session.query(Users).filter_by(id=student_id).one()
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    grade = session.query(Grades).filter_by(teacher_id=teacher_id, num=student.grade).one()
    genre = session.query(Genres).join(Grades).filter_by(teacher_id=teacher_id)
    books = session.query(Books).filter_by(user_id=student_id)
#    creator = getUserInfo(restaurant.user_id)
#    if 'username' not in login_session or creator.id != login_session['user_id']:
#        return render_template('publicmenu.html',
#                               items = items,
#                               restaurant = restaurant,
#                               creator = creator)
#    else:
    print student
    print genre
    return render_template('student.html',
                           student = student,
                           books = books,
                           grade = grade,
                           genre = genre,
                           student_id = student_id,
                           teacher_id = teacher_id)

# Add a student book.
@app.route('/student/<int:student_id>/book/add', methods=['GET', 'POST'])
def newbook(student_id):
    student = session.query(Users).filter_by(id=student_id).one()
    if request.method == 'POST':
        new = Books(title = request.form['title'],
                    author = request.form['author'],
                    image = request.form['image'],
                    review = request.form['review'],
                    genre = request.form['genre'],
                    user_id = student_id
                    )
        session.add(new)
        session.commit()
        flash(new.title + " added!")
        return redirect(url_for('student', student_id=student.id, teacher_id=student.teacher_id))
    else:
        return render_template('newbook.html',
                               student_id = student_id,
                               student = student)

# Edit a student book
@app.route('/student/<int:student_id>/book/<int:book_id>/edit', methods=['GET', 'POST'])
def editbook(student_id, book_id):
    student = session.query(Users).filter_by(id=student_id).one()
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
        return redirect(url_for('student', student_id=student.id, teacher_id=student.teacher_id))
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
    student = session.query(Users).filter_by(id=student_id).one()
#    if school.user_id != login_session['user_id']:
#        return "<script>function myFunction() {alert('You are not authorized to delete this restaurant.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(book)
        session.commit()
        flash(book.title + " deleted!")
        return redirect(url_for('student',
                                student_id = student.id,
                                teacher_id = student.teacher_id))
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
