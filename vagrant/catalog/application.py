from flask import Flask, render_template, url_for, request, redirect, flash
from flask import jsonify
from books_setup import (Schools, Admins, Teachers, Classrooms, Students,
                         Books, Genres, Base)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# For OAuth
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

# For API endpoints
import json
from xml.etree.ElementTree import Element, SubElement, tostring
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = '40 Books'

app = Flask(__name__)


# Connect to Database and create database session
engine = create_engine('sqlite:///book.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


'''
Login and OAuth Block
'''

@app.route('/login')
def login():
    """Create token to prevent forgery and Store in session."""
    login_session['pass'] = 'initial'
    state = randomcsrf()
    login_session['state'] = state
    print login_session['pass']
    return render_template('login.html', STATE=state)

def newadmin(login_session):
    """Add admin for new login."""
    new = Admins(name = login_session['username'],
                   email = login_session['email'],
                   picture = login_session['picture'])
    session.add(new)
    session.commit()
    user = session.query(Admins).filter_by(email = login_session['email']).one()
    return user.id
'''
# Check this
def getuserinfo(user_id):
    user = session.query(Schools).filter_by(id = user_id).one()
    return user

# Check this
def getadmin(school_id):
    user = session.query(Schools).filter_by(id = school_id).one()
    return user.admin_id
'''
def getadmininfo(user_id):
    """Return school admin."""
    school = session.query(Schools).filter_by(id = user_id).one()
    user = session.query(Admins).filter_by(id = school.admin_id).one()
    return user

def credentials(admin, teacher, student):
    """Check whether login user belongs to school via email."""
    if 'username' not in login_session:
        return "false"
    admin = admin
    teacher = teacher
    student = student
    if admin == login_session['email']:
        return "true"
    if teacher == login_session['email']:
        return "true"
    if student == login_session['email']:
        return "true"
    else:
        return "false"

def getuserID(email):
    """Get id if exists and add picture if different in session."""
    try:
        user = session.query(Admins).filter_by(email=email).one()
        if user is not None:
            if user.picture != login_session['picture']:
                user.picture = login_session['picture']
                session.add(user)
                session.commit()
                user = session.query(Admins).filter_by(email=email).one()
        return user.id
    except:
        try:
            user = session.query(Teachers).filter_by(email=email).one()
            if user is not None:
                if user.picture != login_session['picture']:
                    user.picture = login_session['picture']
                    session.add(user)
                    session.commit()
                    user = session.query(Teachers).filter_by(email=email).one()
            return user.id
        except:
            try:
                user = session.query(Students).filter_by(email=email).one()
                if user is not None:
                    if user.picture != login_session['picture']:
                        user.picture = login_session['picture']
                        session.add(user)
                        session.commit()
                        user = (session.query(Students)
                                .filter_by(email=email).one())
                return user.id
            except:
                return None

@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Login via Google Plus or Google Education OAuth."""
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
    login_session['pass'] = '1'
    # Display welcome
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style="width: 200px; height: 200px; border-radius: 150px;'
    output += ' -webkit-border-radius: 150px; -moz-border-radius: 150px;">'
    flash("Logged in as %s" %login_session['username'])
    print 'done!'
    return output

@app.route('/gdisconnect')
def gdisconnect():
    """Disconnect Google Plus or Google Education login."""
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

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Login via Facebook OAuth."""
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
    login_session['access_token'] = token
    login_session['pass'] = '1'
    # Get user picture
    url = 'https://graph.facebook.com/v2.5/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data['data']['url']
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
    output += '" style="width: 200px; height: 200px; border-radius: 150px;'
    output += ' -webkit-border-radius: 150px; -moz-border-radius: 150px;">'
    flash("Logged in as %s" %login_session['username'])
    print 'done!'
    return output

@app.route('/fbdisconnect')
def fbdisconnect():
    """Disconnect Facebook OAuth Login."""
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permission?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return 'You have been logged out.'

# Disconnect Login
@app.route('/disconnect')
def disconnect():
    """Disconnect Login Session Generic Variables."""
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
        del login_session['pass']
        flash('You have successfully logged out.')
        return redirect(url_for('schools'))
    else:
        flash('You were not logged in!')
        return redirect(url_for('schools'))


'''
CSRF Protect Block
'''
def randomcsrf():
    """Create random string for tokens."""
    rstring = (
        ''.join(random.choice(string.ascii_uppercase + string.digits)
                for x in xrange(32))
        )
    print rstring
    return rstring

@app.before_request
def csrf_protect():
    """Check tokens for Posts to prevent CSRF, ignore login post."""
    if request.method == "POST":
        if login_session['pass'] != 'initial':
            token = login_session.pop('_csrf_token', None)
            if not token or token != request.form.get('_csrf_token'):
                response = make_response(json.dumps('Invalid token.'), 403)
                response.headers['Content-Type'] = 'application/json'
                return response

def gentoken():
    """Create CSRF prevention token per post request."""
    if '_csrf_token' not in login_session:
        login_session['_csrf_token'] = randomcsrf()
    return login_session['_csrf_token']

app.jinja_env.globals['gentoken'] = gentoken


'''
JSON Endpoint Block
'''
@app.route('/schools/JSON')
def schoolsJSON():
    """Make JSON API Endpoint for all schools (GET)."""
    schools = session.query(Schools).order_by(Schools.name).all()
    return jsonify(Schools=[i.serialize for i in schools])

@app.route('/school/teachers/<int:school_id>/JSON')
def teachersJSON(school_id):
    """Make JSON API Endpoint for a specific school's teachers (GET)."""
    teachers = (session.query(Teachers)
                .filter_by(school_id=school_id)
                .outerjoin(Classrooms)
                .order_by(Teachers.name).all())
    return jsonify(Teachers=[i.serialize for i in teachers])

@app.route('/school/students/<int:school_id>/JSON')
def studentsJSON(school_id):
    """Make JSON API Endpoint for a specific school's students (GET)."""
    students = (session.query(Students)
                .filter_by(school_id=school_id)
                .order_by(Students.name).all())
    return jsonify(Students=[i.serialize for i in students])

@app.route('/student/books/<int:student_id>/JSON')
def studentlistJSON(student_id):
    """Make JSON API Endpoint for a specific student's book list (GET)."""
    books = (session.query(Books)
                .filter_by(student_id=student_id)
                .order_by(Books.genre, Books.title).all())
    return jsonify(Books=[i.serialize for i in books])

@app.route('/school/student/books/<int:school_id>/JSON')
def schoolbooksJSON(school_id):
    """Make JSON API Endpoint for a school's student book lists (GET)"""
    books = (session.query(Books).outerjoin(Students)
                 .filter_by(school_id=school_id)
                 .order_by(Students.name, Books.genre, Books.title))
    return jsonify(Books=[i.serialize for i in books])

'''
XML Endpoint Block
'''
@app.route('/schools/XML')
def schoolsXML():
    """Make XML API Endpoint for all schools (GET)"""
    schools = session.query(Schools).order_by(Schools.name).all()
    root = Element('Schools')
    for school in schools:
        number = SubElement(root, "School")
        child = SubElement(number, 'id')
        child.text = str(school.id)
        child = SubElement(number, 'name')
        child.text = school.name
    return app.response_class(tostring(root), mimetype='application/xml')

@app.route('/school/<int:school_id>/XML')
def teachersXML(school_id):
    """Make XML API Endpoint for a specific school's teachers (GET)."""
    teachers = (session.query(Teachers)
                .filter_by(school_id=school_id)
                .order_by(Teachers.name).all())
    school = session.query(Schools).filter_by(id=school_id).one()
    root = Element('School')
    for teacher in teachers:
        teach = SubElement(root, 'teacher')
        child = SubElement(teach, 'id')
        child.text = str(teacher.id)
        child = SubElement(teach, 'name')
        child.text = teacher.name
    return app.response_class(tostring(root), mimetype='application/xml')

@app.route('/school/students/<int:school_id>/XML')
def studentsXML(school_id):
    """Make XML API Endpoint for a specific school's students (GET)."""
    students = (session.query(Students)
                .filter_by(school_id=school_id)
                .order_by(Students.classroom, Students.name).all())
    school = session.query(Schools).filter_by(id=school_id).one()
    root = Element('School')
    root.text = school.name
    for student in students:
        each = SubElement(root, "Student")
        # Except for student not yet placed in a class.
        child = SubElement(each, 'Grade')
        try:
            child.text = str(student.classes.grade)
        except:
            child.text = 'Unclassified'
        child = SubElement(each, 'Class')
        try:
            child.text = student.classes.name
        except:
            child.text = 'No Class Listed'
        child = SubElement(each, 'ID')
        child.text = str(student.id)
        child = SubElement(each, 'Name')
        child.text = student.name
    return app.response_class(tostring(root), mimetype='application/xml')

@app.route('/student/books/<int:student_id>/XML')
def studentbooksXML(student_id):
    """Make XML API Endpoint for a specific student's book list (GET)."""
    books = (session.query(Books)
                .filter_by(student_id=student_id)
                .order_by(Books.genre, Books.title).all())
    student = session.query(Students).filter_by(id=student_id).one()
    root = Element('Student')
    root.text = student.name
    for book in books:
        each = SubElement(root, 'Book')
        child = SubElement(each, 'Genre')
        child.text = book.genre
        child = SubElement(each, 'Title')
        child.text = book.title
        child = SubElement(each, 'Author')
        child.text = book.author
        child = SubElement(each, 'Review')
        child.text = book.review
    return app.response_class(tostring(root), mimetype='application/xml')

@app.route('/school/student/books/<int:school_id>/XML')
def schoolbooksXML(school_id):
    """Make XML API Endpoint for specific school's student book lists (GET)."""
    books = (session.query(Books).outerjoin(Students)
                 .filter_by(school_id=school_id)
                 .order_by(Students.name, Books.genre, Books.title))
    students = session.query(Students).filter_by(school_id=school_id).all()
    school = session.query(Schools).filter_by(id=school_id).one()
    root = Element('School')
    root.text = school.name
    for student in students:
        each = SubElement(root, 'Student')
        each.text = student.name
        for book in books:
            if book.student_id == student.id:
                sub = SubElement(each, 'Book')
                child = SubElement(sub, 'Genre')
                child.text = book.genre
                child = SubElement(sub, 'Title')
                child.text = book.title
                child = SubElement(sub, 'Author')
                child.text = book.author
                child = SubElement(sub, 'Review')
                child.text = book.review
    return app.response_class(tostring(root), mimetype='application/xml')

@app.route('/student/books/XML')
def recentbooksXML():
    """Make XML API Endpoint for most recent student book lists (GET)."""
    books = session.query(Books).order_by(Books.id.desc()).limit(10).all()
    root = Element('Forty_Books_App')
    for book in books:
        student = (session.query(Students)
                   .filter_by(id=book.student_id)
                   .one())
        each = SubElement(root, 'School')
        each.text = student.school.name
        each = SubElement(root, 'Student')
        each.text = student.name
        sub = SubElement(each, 'Book')
        child = SubElement(sub, 'ID')
        child.text = str(book.id)
        child = SubElement(sub, 'Genre')
        child.text = book.genre
        child = SubElement(sub, 'Title')
        child.text = book.title
        child = SubElement(sub, 'Author')
        child.text = book.author
        child = SubElement(sub, 'Review')
        child.text = book.review
        child = SubElement(sub, 'Date')
        child.text = str(book.date)
    return app.response_class(tostring(root), mimetype='application/xml')

'''
Atom/RSS
'''
@app.route('/recent.atom')
def recent_feed():
    """Make Atom/RSS feed for most recent student book lists (GET)."""
    feed = AtomFeed('Recent Books',
                    feed_url=request.url, url=request.url_root)
    books = session.query(Books).order_by(Books.id.desc()).limit(10).all()
    for book in books:
        student = session.query(Students).filter_by(id=book.student_id).one()
        feed.add(book.title,
                 book.review,
                 content_type='html',
                 author=student.name,
                 url=('/' +str(student.classes.teacher_id)
                      +'/student/' + str(student.id)),
                 id=book.id,
                 updated=book.date,
                 published=book.date)
    return feed.get_response()

def make_external(url):
    return urljoin(request.url_root, url)


'''
School Block
'''
@app.route('/')
@app.route('/schools')
def schools():
    """Return all schools in DB."""
    schools = session.query(Schools).order_by(Schools.name).all()
    if 'username' not in login_session:
        return render_template('public/schools.html',
                               schools=schools)
    student = session.query(Students).filter_by(email=login_session['email'])
    # Do not show add school function if user is a registered student.
    if student ==[]:
            return render_template('public/schools.html',
                               schools=schools)
    else:
        return render_template('schools.html',
                           schools=schools)

@app.route('/school/<int:school_id>')
def school(school_id):
    """Return a specific school with students and teachers."""
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

@app.route('/school/new', methods=['GET', 'POST'])
def newschool():
    """Create a new school."""
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

@app.route('/school/<int:school_id>/edit', methods=['GET', 'POST'])
def editschool(school_id):
    """Edit an existing school (admin only)."""
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

@app.route('/school/<int:school_id>/delete', methods=['GET', 'POST'])
def deleteschool(school_id):
    """Delete an existing school (admin only)."""
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

@app.route('/school/<int:school_id>/teachers')
def schoolteachers(school_id):
    """Return a specific school's teachers."""
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

@app.route('/school/<int:school_id>/students')
def schoolstudents(school_id):
    """Return a specific school's students."""
    school = session.query(Schools).filter_by(id=school_id).one()
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
@app.route('/school/<int:school_id>/teacher/new', methods=['GET', 'POST'])
def newteacher(school_id):
    """Create a new teacher (admin only)."""
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

@app.route('/school/<int:school_id>/teacher/<int:teacher_id>/edit',
           methods=['GET', 'POST'])
def editteacher(school_id, teacher_id):
    """Edit an existing teacher (admin and edited teacher only)."""
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    creator = getadmininfo(school_id)
    check = credentials(creator.email, teacher.email, 0)
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

@app.route('/school/<int:school_id>/teacher/<int:teacher_id>/delete',
           methods=['GET', 'POST'])
def deleteteacher(school_id, teacher_id):
    """Delete an existing teacher (admin only)."""
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
@app.route('/teacher/<int:teacher_id>/classroom')
def classroom(teacher_id):
    """Return a teacher's classrooms."""
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
    if credcheck != "true":
        return render_template('public/classes.html',
                               teacher = teacher,
                               students = students,
                               classroom = classroom,
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

@app.route('/teacher/<int:teacher_id>/classroom/<int:room_id>')
def room(teacher_id, room_id):
    """Return a specific classroom."""
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

@app.route('/teacher/<int:teacher_id>/classroom/new', methods=['GET', 'POST'])
def newclass(teacher_id):
    """Create a classroom (admin and teacher only)."""
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

@app.route('/teacher/<int:teacher_id>/classroom/<int:class_id>/edit',
           methods=['GET', 'POST'])
def editclass(teacher_id, class_id):
    """Edit an existing classroom (admin and teacher only)."""
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
            if request.form['set'] == "clear":
                classroom.set_id = ""
            else:
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

@app.route('/teacher/<int:teacher_id>/classroom/<int:class_id>/delete',
           methods=['GET', 'POST'])
def deleteclass(teacher_id, class_id):
    """Delete an existing classroom (admin and teacher only)."""
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
@app.route('/teacher/<int:teacher_id>/genrelists')
def genre(teacher_id):
    """Return a teacher's genre lists."""
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

@app.route('/teacher/<int:teacher_id>/genrelist/new', methods=['GET', 'POST'])
def newlist(teacher_id):
    """Create a new genre list (admin and teacher only)."""
    if 'username' not in login_session:
        return redirect('/login')
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    creator = getadmininfo(teacher.school_id)
    credcheck = credentials(creator.email, teacher.email, 0)
    if 'username' not in login_session or credcheck != "true":
        return ('''
                   <script>
                    function myFunction() {
                    alert('You are not authorized to add a list to this
                           school.');
                    }
                    </script>
                    <body onload='myFunction()''>
                ''')
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

@app.route('/teacher/<int:teacher_id>/genrelist/<int:list_id>/edit',
           methods=['GET', 'POST'])
def editlist(teacher_id, list_id):
    """Edit an existing genre list (admin and teacher only)."""
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

@app.route('/teacher/<int:teacher_id>/genrelist/<int:list_id>/delete',
           methods=['GET', 'POST'])
def deletelist(teacher_id, list_id):
    """Delete an existing genre list (admin and teacher only)."""
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
@app.route('/school/<int:school_id>/student/new', methods=['GET', 'POST'])
def newstudent(school_id):
    """Create a new student from school list (admin only)."""
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
        if request.form['classroom'] != "clear":
            room = request.form['classroom']
        else:
            room = "0"
        new = Students(name=request.form['name'],
                    email=request.form['email'],
                    picture=request.form['picture'],
                    classroom=room,
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

# Allow student creation from within a classroom.
@app.route('/school/<int:school_id>/teacher/<int:teacher_id>/student/new',
           methods=['GET', 'POST'])
def teachernewstudent(school_id, teacher_id):
    """Create a new student (admin and teacher only)."""
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(Schools).filter_by(id=school_id).one()
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    classes = session.query(Classrooms).filter_by(school_id=school_id)
    creator = getadmininfo(school_id)
    credcheck = credentials(creator.email, teacher.email, 0)
    if 'username' not in login_session or credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to add a student to this
                           school.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
    if request.method == 'POST':
        if request.form['classroom'] != "clear":
            room = request.form['classroom']
        else:
            room = "0"
        new = Students(name=request.form['name'],
                    email=request.form['email'],
                    picture=request.form['picture'],
                    classroom=room,
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

@app.route('/school/<int:school_id>/student/<int:user_id>/edit',
           methods=['GET', 'POST'])
def editstudent(school_id, user_id):
    """Edit an existing student from school list (admin only)."""
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
            if request.form['classroom'] == "clear":
                student.classroom = "0"
            else:
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

# Allow student edit from within a classroom.
@app.route('/<int:school_id>/<int:teacher_id>/student/<int:user_id>/edit',
           methods=['GET', 'POST'])
def teachereditstudent(school_id, user_id, teacher_id):
    """Edit an existing student from classroom (admin and teacher only)."""
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
            if request.form['classroom'] == "clear":
                student.classroom = "0"
            else:
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

@app.route('/school/<int:school_id>/student/<int:user_id>/delete',
           methods=['GET', 'POST'])
def deletestudent(school_id, user_id):
    """Delete an existing student from school list (admin only)."""
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

# Allow student deletion from within classroom.
@app.route('/<int:school_id>/<int:teacher_id>/student/<int:user_id>/delete',
           methods=['GET', 'POST'])
def teacherdeletestudent(school_id, user_id, teacher_id):
    """Delete an existing student from classroom (admin and teacher only)."""
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
@app.route('/<int:teacher_id>/student/<int:student_id>')
def student(student_id, teacher_id):
    """Return a student's books"""
    student = session.query(Students).filter_by(id=student_id).one()
    genre = (session.query(Genres)
             .join(Classrooms)
             .filter(Classrooms.id==student.classroom))
    books = session.query(Books).filter_by(student_id=student_id)
    num = books.count()
    percent = (num*100)/40
    # Count each genre listing of books.
    poetry = books.filter_by(genre='poetry').count()
    graph = books.filter_by(genre='graphic').count()
    real = books.filter_by(genre='realistic').count()
    hist = books.filter_by(genre='historical').count()
    fan = books.filter_by(genre='fantasy').count()
    sci = books.filter_by(genre='scifi').count()
    myst = books.filter_by(genre='mystery').count()
    info = books.filter_by(genre='info').count()
    bio = books.filter_by(genre='bio').count()
    school = session.query(Schools).filter_by(id=student.school_id).one()
    teacher = session.query(Teachers).filter_by(id=teacher_id).one()
    creator = getadmininfo(student.school_id)
    credcheck = credentials(creator.email, teacher.email, student.email)
    if credcheck != "true":
        return render_template('public/student.html',
                               student = student,
                               books = books,
                               percent = percent,
                               genre = genre,
                               poetry = poetry,
                               graph = graph,
                               real = real,
                               hist = hist,
                               fan = fan,
                               sci = sci,
                               myst = myst,
                               info = info,
                               bio = bio,
                               school = school,
                               student_id = student_id,
                               teacher_id = teacher_id)
    else:
        return render_template('student/student.html',
                               student = student,
                               books = books,
                               genre = genre,
                               percent = percent,
                               poetry = poetry,
                               graph = graph,
                               real = real,
                               hist = hist,
                               fan = fan,
                               sci = sci,
                               myst = myst,
                               info = info,
                               bio = bio,
                               school = school,
                               student_id = student_id,
                               teacher_id = teacher_id)

@app.route('/student/<int:student_id>/book/add', methods=['GET', 'POST'])
def newbook(student_id):
    """Create a book entry (admin, teacher, student)."""
    if 'username' not in login_session:
        return redirect('/login')
    student = session.query(Students).filter_by(id=student_id).one()
    teacher = (session.query(Teachers)
               .filter_by(id=student.classes.teacher_id).one())
    creator = getadmininfo(student.school_id)
    credcheck = credentials(creator.email, teacher.email, student.email)
    if credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to add a book for this
                          student.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
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

@app.route('/student/<int:student_id>/book/<int:book_id>/edit',
           methods=['GET', 'POST'])
def editbook(student_id, book_id):
    """Edit an existing book entry (admin, teacher, student)."""
    if 'username' not in login_session:
        return redirect('/login')
    student = session.query(Students).filter_by(id=student_id).one()
    book = session.query(Books).filter_by(id=book_id).one()
    teacher = (session.query(Teachers)
               .filter_by(id=student.classes.teacher_id).one())
    creator = getadmininfo(student.school_id)
    credcheck = credentials(creator.email, teacher.email, student.email)
    if credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to edit a book for this
                          student.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
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
        return redirect(url_for('student',
                                student_id=student.id,
                                teacher_id=student.classes.teacher_id))
    else:
        return render_template('book/edit.html',
                               student_id = student_id,
                               book_id = book_id,
                               student = student,
                               book = book)

@app.route('/student/<int:student_id>/book/<int:book_id>/delete',
           methods=['GET', 'POST'])
def deletebook(student_id, book_id):
    """Delete an existing book entry (admin, teacher, student)."""
    if 'username' not in login_session:
        return redirect('/login')
    book = session.query(Books).filter_by(id=book_id).one()
    student = session.query(Students).filter_by(id=student_id).one()
    teacher = (session.query(Teachers)
               .filter_by(id=student.classes.teacher_id).one())
    creator = getadmininfo(student.school_id)
    credcheck = credentials(creator.email, teacher.email, student.email)
    if credcheck != "true":
        return ('''
                    "<script>
                    function myFunction() {
                    alert('You are not authorized to delete a book for this
                          student.');
                    }
                    </script>
                    <body onload='myFunction()''>"
                ''')
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
