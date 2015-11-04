from flask import Flask, render_template, url_for, request, redirect, flash
from flask import jsonify
from books_setup import Schools, Admins, Teachers, Classrooms, Students, Books, Genres, Base
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

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = '40 Books'

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///book.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a state token to prevent request forgery
# Store the token in session for validation
@app.route('/login')
def login():
    state = (
        ''.join(random.choice(string.ascii_uppercase + string.digits)
                for x in xrange(32))
        )
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Add admin if does not exist.
def newadmin(login_session):
    new = Admins(name = login_session['username'],
                   email = login_session['email'],
                   picture = login_session['picture'])
    session.add(new)
    session.commit()
    user = session.query(Admins).filter_by(email=login_session['email']).one()
    return user.id

# Check this
def getuserinfo(user_id):
    user = session.query(Schools).filter_by(id=user_id).one()
    return user

# Check this
def getadmin(school_id):
    user = session.query(Schools).filter_by(id=school_id).one()
    return user.admin_id

# Return school admin.
def getadmininfo(user_id):
    school = session.query(Schools).filter_by(id=user_id).one()
    user = session.query(Admins).filter_by(id=school.admin_id).one()
    return user

# Check whether a user belongs to a school.
def credentials(admin, teacher, student):
    if admin != login_session['email']:
        if teacher != login_session['email']:
            if student != login_session['email']:
                return "false"
            else:
                return "true"
        else:
            return "true"
    else:
        return "true"

# Get login_session DB id, if exists
def getuserID(email):
    try:
        user = session.query(Admins).filter_by(email=email).one()
        return user.id
    except:
        try:
            user = session.query(Teachers).filter_by(email=email).one()
            return user.id
        except:
            try:
                user = session.query(Students).filter_by(email=email).one()
                return user.id
            except:
                return None

# Google Plus and Google Education OAuth
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain Auth code.
    code = request.data
    try:
        # Upgrade authorization code to a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the auth code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check access token.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If any error in token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # Verify the token is for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps('Token user ID does not match given user ID'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify the access token is valid for app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps('Token client ID does not match given client ID'), 401)
        print 'Token client ID does not match app ID.'
        response.headers['Content-type'] = 'application/json'
        return response
    # Check whether user is already logged in.
    stored_credentials = login_session.get('gplus_id')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store access token for later use in the session.
    login_session['provider'] = 'google'
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    # Get user info.
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # Check whether user exists in database.
    user_id = getuserID(login_session['email'])
    if not user_id:
        user_id = newadmin(login_session)
    login_session['user_id'] = user_id
    # Display welcome
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style="width: 300px; height: 300px; border-radius: 150px;'
    output += ' -webkit-border-radius: 150px; -moz-border-radius: 150px;">'
    flash("Logged in as %s" %login_session['username'])
    print 'done!'
    return output

# Disconnect Google Plus - Revoke token and reset session.
@app.route('/gdisconnect')
def gdisconnect():
    # Disconnect a connected user.
    credentials = login_session.get('credentials')
    # If not connected, say so.
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Revoke token if connected.
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        response = make_response(json.dumps('Failed to revoke token.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

# Facebook OAuth
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print 'access token received %s' % access_token
    # Exchange token for long-lived server-side token.
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print result
    # Use token to get user info from API
    userinfo_url = 'https://graph.facebook.com/v2.5/me'
    # Strip expire tag from access token.
    token = result.split("&")[0]
    url = 'https://graph.facebook.com/v2.5/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print 'url sent for API access: %s' % url
    # print 'API JSON result: %s' % result
    data = json.loads(result)
    # Transfer user info to session.
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    # Get user picture
    url = 'https://graph.facebook.com/v2.5/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data['data']['url']
    # Check whether user exists in database.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    # Display welcome
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style="width: 300px; height: 300px; border-radius: 150px;'
    output += ' -webkit-border-radius: 150px; -moz-border-radius: 150px;">'
    flash("Logged in as %s" %login_session['username'])
    print 'done!'
    return output

# Disconnect Facebook - Revoke token and reset session
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permission?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return 'You have been logged out.'

# Disconnect Login
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash('You have successfully logged out.')
        return redirect(url_for('schools'))
    else:
        flash('You were not logged in!')
        return redirect(url_for('schools'))

# Show all schools
@app.route('/')
@app.route('/schools')
def schools():
    schools = session.query(Schools).order_by(Schools.name).all()
    if 'username' not in login_session:
        return render_template('pubschools.html',
                               schools=schools)
    student = session.query(Students).filter_by(email=login_session['email'])
    # Do not show add school function if user is a registered student.
    if student ==[]:
            return render_template('public/schools.html',
                               schools=schools)
    else:
        return render_template('schools.html',
                           schools=schools)

# Show a specific school.
@app.route('/school/<int:school_id>')
def school(school_id):
    school = session.query(Schools).filter_by(id=school_id).one()
    students = (session.query(Students)
                .filter_by(school_id=school_id)
                .order_by(Students.name))
    teachers = (session.query(Teachers)
                .filter_by(school_id=school_id)
                .order_by(Teachers.name))
    books = (session.query(Books)
             .join(Students)
             .filter(Students.school_id==school_id)
             .all())
    creator = getadmininfo(school_id)
    if ('username' not in login_session or
        creator.email != login_session['email']):
        return render_template('public/school.html',
                               school = school,
                               students = students,
                               books = books,
                               teachers = teachers,
                               school_id = school_id)
    else:
        return render_template('school/school.html',
                               school = school,
                               students = students,
                               books = books,
                               teachers = teachers,
                               school_id = school_id)

# Create a new school
@app.route('/school/new', methods=['GET', 'POST'])
def newschool():
    # Check login.
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new = Schools(name=request.form['name'],
                      state=request.form['state'],
                      county=request.form['county'],
                      district=request.form['district'],
                      admin_id=login_session['user_id']
        )
        session.add(new)
        session.commit()
        flash(new.name + " created!")
        return redirect(url_for('schools'))
    else:
        return render_template('school/new.html')

# Edit a school
@app.route('/school/<int:school_id>/edit', methods=['GET', 'POST'])
def editschool(school_id):
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    creator = getadmininfo(school_id)
    if creator.email != login_session['email']:
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to edit this school.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
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
        return render_template('school/edit.html',
                               school_id = school_id,
                               school = school)

# Delete a school
@app.route('/school/<int:school_id>/delete', methods=['GET', 'POST'])
def deleteschool(school_id):
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    creator = getadmininfo(school_id)
    if creator.email != login_session['email']:
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to delete this school.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
    if request.method == 'POST':
        session.delete(school)
        session.commit()
        flash(school.name + " deleted!")
        return redirect(url_for('schools'))
    else:
        return render_template('school/delete.html',
                               school = school,
                               school_id = school_id)

# Show a specific school's teachers
@app.route('/school/<int:school_id>/teachers')
def schoolteachers(school_id):
    school = session.query(Schools).filter_by(id=school_id).one()
    teachers = session.query(Teachers).filter_by(school_id=school_id)
    school = session.query(Schools).filter_by(id=school_id).one()
    creator = getadmininfo(school_id)
    if ('username' not in login_session or
        creator.email != login_session['email']):
        return render_template('public/teachers.html',
                               school = school,
                               teachers = teachers,
                               school_id = school_id)
    else:
        return render_template('school/teachers.html',
                               school = school,
                               teachers = teachers,
                               school_id = school_id)

# Show a specific school's students.
@app.route('/school/<int:school_id>/students')
def schoolstudents(school_id):
    school = session.query(Schools).filter_by(id=school_id).one()
#    grades = (session.query(Students)
#                .filter_by(school_id=school_id)
#                .order_by(Students.name)
#                .all())
    students = session.query(Students).filter_by(school_id=school_id).all()
    creator = getadmininfo(school_id)
    credcheck = credentials(creator.email, 0, 0)
    if 'username' not in login_session or credcheck != "true":
        return render_template('public/students.html',
                               school = school,
                               students = students,
                               school_id = school_id)
    else:
        return render_template('school/students.html',
                               school = school,
                               students = students,
                               school_id = school_id)

'''
Teacher Block
'''
# Add a teacher.
@app.route('/school/<int:school_id>/teacher/new', methods=['GET', 'POST'])
def newteacher(school_id):
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    creator = getadmininfo(school_id)
    if creator.email != login_session['email']:
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to add a teacher to this
                          school.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
    if request.method == 'POST':
        new = Teachers(name=request.form['name'],
                       email=request.form['email'],
                       picture=request.form['picture'],
                       school_id=school_id
        )
        session.add(new)
        session.commit()
        flash(new.name + " added!")
        return redirect(url_for('schoolteachers', school_id = school_id))
    else:
        return render_template('teacher/new.html',
                               school_id = school_id,
                               school = school)

# Edit a teacher.
@app.route('/school/<int:school_id>/teacher/<int:teacher_id>/edit',
           methods=['GET', 'POST'])
def editteacher(school_id, teacher_id):
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    creator = getadmininfo(school_id)
    check = credentials(creator.email, teacher.email, 0)
#    if creator.email != login_session['email']:
    if check != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to edit a teacher of this
                          school.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
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
        return redirect(url_for('schoolteachers', school_id = school_id))
    else:
        return render_template('teacher/edit.html',
                               school_id = school_id,
                               teacher_id = teacher_id,
                               teacher = teacher,
                               school = school)

# Delete a teacher.
@app.route('/school/<int:school_id>/teacher/<int:teacher_id>/delete',
           methods=['GET', 'POST'])
def deleteteacher(school_id, teacher_id):
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    creator = getadmininfo(school_id)
    if creator.email != login_session['email']:
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to delete a teacher of this
                          school.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
    if request.method == 'POST':
        session.delete(teacher)
        session.commit()
        flash(teacher.name + " deleted!")
        return redirect(url_for('schoolteachers', school_id = school_id))
    else:
        return render_template('teacher/delete.html',
                               school = school,
                               teacher = teacher,
                               teacher_id = teacher_id,
                               school_id = school_id)

'''
Class(es) Block
'''
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
    lists = session.query(Genres).filter_by(teacher_id=teacher_id).all()
    books = (session.query(Books)
             .join(Students)
             .join(Classrooms)
             .filter_by(teacher_id=teacher_id).all())
    creator = getadmininfo(teacher.school_id)
    credcheck = credentials(creator.email, teacher.email, 0)
    if 'username' not in login_session or credcheck != "true":
        return render_template('public/classes.html',
                               teacher = teacher,
                               students = students,
                               classroom = classroom,
                               noclass = noclass,
                               lists = lists,
                               books = books,
                               teacher_id = teacher_id)
    else:
        return render_template('class/classes.html',
                               teacher = teacher,
                               students = students,
                               classroom = classroom,
                               noclass = noclass,
                               lists = lists,
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
             .filter(Students.classroom == room_id).all())
    creator = getadmininfo(teacher.school_id)
    credcheck = credentials(creator.email, teacher.email, 0)
    if 'username' not in login_session or credcheck != "true":
        return render_template('public/classroom.html',
                           teacher = teacher,
                           students = students,
                           books = books,
                           classroom = classroom,
                           classother = classother,
                           teacher_id = teacher_id,
                           room_id = room_id)
    else:
        return render_template('class/classroom.html',
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
    if 'username' not in login_session:
        return redirect('/login')
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    classes = (session.query(Classrooms)
              .filter_by(teacher_id=teacher_id)
              .order_by(Classrooms.grade, Classrooms.name))
    sets = session.query(Genres).filter_by(teacher_id=teacher_id).all()
    creator = getadmininfo(teacher.school_id)
    credcheck = credentials(creator.email, teacher.email, 0)
    if 'username' not in login_session or credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to add a classroom to this
                          school.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
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
        return render_template('class/new.html',
                               teacher = teacher,
                               classes = classes,
                               sets = sets,
                               teacher_id = teacher_id)

# Edit a classroom.
@app.route('/teacher/<int:teacher_id>/classroom/<int:class_id>/edit',
           methods=['GET', 'POST'])
def editclass(teacher_id, class_id):
    if 'username' not in login_session:
        return redirect('/login')
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    grades = (session.query(Classrooms)
              .filter_by(teacher_id=teacher_id)
              .order_by(Classrooms.grade, Classrooms.name))
    allteach = session.query(Teachers).filter_by(school_id=teacher.school_id)
    classroom = session.query(Classrooms).filter_by(id=class_id).one()
    sets = session.query(Genres).filter_by(teacher_id=teacher_id).all()
    creator = getadmininfo(teacher.school_id)
    credcheck = credentials(creator.email, teacher.email, 0)
    if 'username' not in login_session or credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to edit a classroom of this
                          school.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
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
        return render_template('class/edit.html',
                               teacher = teacher,
                               grades = grades,
                               classroom = classroom,
                               sets = sets,
                               allteach = allteach,
                               teacher_id = teacher_id,
                               class_id = class_id)

# Delete a classroom.
@app.route('/teacher/<int:teacher_id>/classroom/<int:class_id>/delete',
           methods=['GET', 'POST'])
def deleteclass(teacher_id, class_id):
    if 'username' not in login_session:
        return redirect('/login')
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    classroom = session.query(Classrooms).filter_by(id=class_id).one()
    creator = getadmininfo(teacher.school_id)
    credcheck = credentials(creator.email, teacher.email, 0)
    if 'username' not in login_session or credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to delete a classroom of this
                          school.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
    if request.method == 'POST':
        session.delete(classroom)
        session.commit()
        flash(classroom.name + " deleted!")
        return redirect(url_for('classroom', teacher_id = teacher_id))
    else:
        return render_template('class/delete.html',
                               teacher = teacher,
                               classroom = classroom,
                               teacher_id = teacher_id,
                               class_id = class_id)

'''
Genre Lists Block
'''
# Show a teacher's genre lists
@app.route('/teacher/<int:teacher_id>/genrelists')
def genre(teacher_id):
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    school = session.query(Schools).filter_by(id=teacher.school_id).one()
    lists = session.query(Genres).filter_by(teacher_id=teacher_id).all()
    classes = session.query(Classrooms).filter_by(teacher_id=teacher_id).all()
    creator = getadmininfo(teacher.school_id)
    credcheck = credentials(creator.email, teacher.email, 0)
    if 'username' not in login_session or credcheck != "true":
        return render_template('public/lists.html',
                               school = school,
                               teacher = teacher,
                               lists = lists,
                               classes = classes,
                               teacher_id = teacher_id)
    else:
        return render_template('genre/lists.html',
                               school = school,
                               teacher = teacher,
                               lists = lists,
                               classes = classes,
                               teacher_id = teacher_id)

# Add a genre list.
@app.route('/teacher/<int:teacher_id>/genrelist/new', methods=['GET', 'POST'])
def newlist(teacher_id):
    if 'username' not in login_session:
        return redirect('/login')
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    creator = getadmininfo(teacher.school_id)
    credcheck = credentials(creator.email, teacher.email, 0)
#    if 'username' not in login_session or credcheck != "true":
#        return ('''
#                    <script>
#                    function myFunction() {
#                    alert('You are not authorized to add a list to this
#                           school.');
#                    }
#                    </script>
#                    <body onload='myFunction()''>
#                ''')
    if request.method == 'POST':
        new = Genres(name=request.form['name'],
                     teacher_id=teacher.id,
                     poetry=request.form['poetry'],
                     graphic=request.form['graphic'],
                     realistic=request.form['realistic'],
                     historical=request.form['historical'],
                     fantasy=request.form['fantasy'],
                     scifi=request.form['scifi'],
                     mystery=request.form['mystery'],
                     info=request.form['info'],
                     bio=request.form['bio'],
                     pages=request.form['pages']
                    )
        session.add(new)
        session.commit()
        flash(new.name + " added!")
        return redirect(url_for('classroom',
                                teacher = teacher,
                                teacher_id=teacher.id))
    else:
        return render_template('genre/new.html',
                               teacher = teacher,
                               teacher_id=teacher.id)

# Edit a genre list.
@app.route('/teacher/<int:teacher_id>/genrelist/<int:list_id>/edit',
           methods=['GET', 'POST'])
def editlist(teacher_id, list_id):
    if 'username' not in login_session:
        return redirect('/login')
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    alist = session.query(Genres).filter_by(id=list_id).one()
    creator = getadmininfo(teacher.school_id)
    credcheck = credentials(creator.email, teacher.email, 0)
    if 'username' not in login_session or credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to edit a list of this
                          school.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
    if request.method == 'POST':
        if request.form['name']:
            alist.name=request.form['name']
        if request.form['poetry']:
            alist.poetry=request.form['poetry']
        if request.form['graphic']:
            alist.graphic=request.form['graphic']
        if request.form['realistic']:
            alist.realistic=request.form['realistic']
        if request.form['historical']:
            alist.historical=request.form['historical']
        if request.form['fantasy']:
            alist.fantasy=request.form['fantasy']
        if request.form['scifi']:
            alist.scifi=request.form['scifi']
        if request.form['mystery']:
            alist.mystery=request.form['mystery']
        if request.form['info']:
            alist.info=request.form['info']
        if request.form['bio']:
            alist.bio=request.form['bio']
        if request.form['pages']:
            alist.pages=request.form['pages']
        session.add(alist)
        session.commit()
        flash(alist.name + " edited!")
        return redirect(url_for('classroom', teacher_id = teacher.id))
    else:
        return render_template('genre/edit.html',
                               alist = alist,
                               teacher = teacher,
                               teacher_id = teacher.id,
                               list_id = alist.id)

# Delete a genre list.
@app.route('/teacher/<int:teacher_id>/genrelist/<int:list_id>/delete',
           methods=['GET', 'POST'])
def deletelist(teacher_id, list_id):
    if 'username' not in login_session:
        return redirect('/login')
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    alist = session.query(Genres).filter_by(id=list_id).one()
    creator = getadmininfo(teacher.school_id)
    credcheck = credentials(creator.email, teacher.email, 0)
    if 'username' not in login_session or credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to delete a list of this
                          school.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
    if request.method == 'POST':
        session.delete(alist)
        session.commit()
        flash(alist.name + " deleted!")
        return redirect(url_for('classroom', teacher_id = teacher.id))
    else:
        return render_template('genre/delete.html',
                               alist = alist,
                               teacher = teacher,
                               teacher_id = teacher.id,
                               list_id = alist.id)

'''
Student Block
'''
# Add a student.
@app.route('/school/<int:school_id>/student/new', methods=['GET', 'POST'])
def newstudent(school_id):
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    teachers = session.query(Teachers).filter_by(school_id=school_id).all()
    classes = session.query(Classrooms).filter_by(school_id=school_id)
    creator = getadmininfo(school_id)
    credcheck = credentials(creator.email, 0, 0)
    if 'username' not in login_session or credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to add a student to this
                           school..');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
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
        return render_template('student/new.html',
                               school_id=school_id,
                               classes = classes,
                               school=school)

# Add student by teacher
@app.route('/school/<int:school_id>/teacher/<int:teacher_id>/student/new',
           methods=['GET', 'POST'])
def teachernewstudent(school_id, teacher_id):
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
#    teachers = session.query(Teachers).filter_by(school_id=school_id).all()
    classes = session.query(Classrooms).filter_by(school_id=school_id)
    creator = getadmininfo(school_id)
    credcheck = credentials(creator.email, teacher.email, 0)
    if 'username' not in login_session or credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to add a student to this
                           school..');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
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
        return redirect(url_for('classroom', teacher_id=teacher_id))
    else:
        return render_template('student/new.html',
                               school_id=school_id,
                               classes = classes,
                               school=school)

# Edit a student.
@app.route('/school/<int:school_id>/student/<int:user_id>/edit',
           methods=['GET', 'POST'])
def editstudent(school_id, user_id):
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    teachers = session.query(Teachers).filter_by(school_id=school_id).all()
    classes = session.query(Classrooms).filter_by(school_id=school_id)
    student = session.query(Students).filter_by(id=user_id).one()
    creator = getadmininfo(school_id)
    credcheck = credentials(creator.email, 0, 0)
    if 'username' not in login_session or credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to edit this student.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
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
        return render_template('student/edit.html',
                               school_id = school_id,
                               user_id = user_id,
                               student = student,
                               classes = classes,
                               teachers = teachers,
                               school = school)

# Edit a student by teacher.
@app.route('/<int:school_id>/<int:teacher_id>/student/<int:user_id>/edit',
           methods=['GET', 'POST'])
def teachereditstudent(school_id, user_id, teacher_id):
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    teachers = session.query(Teachers).filter_by(school_id=school_id).all()
    classes = session.query(Classrooms).filter_by(school_id=school_id)
    student = session.query(Students).filter_by(id=user_id).one()
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    creator = getadmininfo(school_id)
    credcheck = credentials(creator.email, teacher.email, 0)
    if 'username' not in login_session or credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to edit this student.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
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
        return redirect(url_for('classroom', teacher_id=teacher_id))
    else:
        return render_template('student/edit.html',
                               school_id = school_id,
                               user_id = user_id,
                               student = student,
                               classes = classes,
                               teachers = teachers,
                               school = school)

# Delete a student
@app.route('/school/<int:school_id>/student/<int:user_id>/delete',
           methods=['GET', 'POST'])
def deletestudent(school_id, user_id):
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    student = session.query(Students).filter_by(id=user_id).one()
    creator = getadmininfo(school_id)
    credcheck = credentials(creator.email, 0, 0)
    if 'username' not in login_session or credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to delete this student.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
    if request.method == 'POST':
        session.delete(student)
        session.commit()
        flash(student.name + " deleted!")
        return redirect(url_for('schoolstudents', school_id = school_id))
    else:
        return render_template('student/delete.html',
                               school = school,
                               student = student,
                               user_id = user_id,
                               school_id = school_id)

# Delete a student by teacher.
@app.route('/<int:school_id>/<int:teacher_id>/student/<int:user_id>/delete',
           methods=['GET', 'POST'])
def teacherdeletestudent(school_id, user_id, teacher_id):
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    student = session.query(Students).filter_by(id=user_id).one()
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    creator = getadmininfo(school_id)
    credcheck = credentials(creator.email, teacher.email, 0)
    if 'username' not in login_session or credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to delete this student.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
    if request.method == 'POST':
        session.delete(student)
        session.commit()
        flash(student.name + " deleted!")
        return redirect(url_for('classroom', teacher_id = teacher_id))
    else:
        return render_template('student/delete.html',
                               school = school,
                               student = student,
                               user_id = user_id,
                               school_id = school_id)

'''
Books Block
'''
# Show a student's books.
@app.route('/<int:teacher_id>/student/<int:student_id>')
def student(student_id, teacher_id):
    student = session.query(Students).filter_by(id=student_id).one()
    genre = (session.query(Genres)
             .join(Classrooms)
             .filter_by(teacher_id=teacher_id))
    books = session.query(Books).filter_by(student_id=student_id)

    return render_template('student/student.html',
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
        return redirect(url_for('student',
                                student_id = student.id,
                                teacher_id = student.classes.teacher_id))
    else:
        return render_template('book/new.html',
                               student_id = student_id,
                               student = student)

# Edit a student book
@app.route('/student/<int:student_id>/book/<int:book_id>/edit',
           methods=['GET', 'POST'])
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
        return render_template('book/edit.html',
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
        return render_template('book/delete.html',
                               student = student,
                               student_id = student_id,
                               book = book,
                               book_id = book_id)


if __name__ == '__main__':
    app.secret_key = 'super-secret-key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
