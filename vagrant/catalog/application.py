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

# Show a specific school's students
@app.route('/school/<int:school_id>/students')
def schoolstudents(school_id):
    school = session.query(Schools).filter_by(id=school_id).one()
    teacher = session.query(Teachers).join(Schools)
    students = (session.query(Users)
                .filter_by(school_id=school_id)
                .order_by(Users.name))
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

@app.route('/school/<int:school_id>/student/new', methods=['GET', 'POST'])
def newstudent(school_id):
    school = session.query(Schools).filter_by(id=school_id).one()
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
                               school=school)

@app.route('/school/<int:school_id>/student/<int:user_id>/edit', methods=['GET', 'POST'])
def editstudent(school_id, user_id):
    school = session.query(Schools).filter_by(id=school_id).one()
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


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
