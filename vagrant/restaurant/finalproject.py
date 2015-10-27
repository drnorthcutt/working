from flask import Flask, render_template, url_for, request, redirect, flash
from flask import jsonify
from restaurant_setup import Base, Restaurant, MenuItem, Users
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
APPLICATION_NAME = 'Restaurant Menu App'

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a state token to prevent request forgery
# Store the token in session for validation
@app.route('/login')
def showLogin():
    state = (
        ''.join(random.choice(string.ascii_uppercase + string.digits)
                for x in xrange(32))
        )
    login_session['state'] = state
    return render_template('login.html', STATE=state)

def createUser(login_session):
    newUser = Users(name = login_session['username'],
                   email = login_session['email'],
                   picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email = login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(Users).filter_by(id = user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(Users).filter_by(email = email).one()
        return user.id
    except:
        return None

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
        response = make_response(json.dumps('Failed to upgrade the auth code.'), 401)
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
        response = make_response(json.dumps('Token user ID does not match given user ID'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify the access token is valid for app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps('Token client ID does not match given client ID'), 401)
        print 'Token client ID does not match app ID.'
        response.headers['Content-type'] = 'application/json'
        return response
    # Check whether user is already logged in.
    stored_credentials = login_session.get('gplus_id')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store access token for later use in the session.
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
    # Display welcome
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style="width: 300px; height: 300px; border-radius: 150px; -webkit-border-radius: 150px; -moz-border-radius: 150px;">'
    flash("Logged in as %s" %login_session['username'])
    print 'done!'
    return output

# Disconnect- Revoke token and reset session.
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
    if result['status'] == '200':
        # Reset user session.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Sucessfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # Do if token invalid.
        response = make_response(json.dumps('Failed to revoke token.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Show all restaurants
@app.route('/')
@app.route('/restaurants')
def allRestaurants():
    # return "All restaurants alphabetical"
    restaurant = session.query(Restaurant).order_by(Restaurant.name).all()
    if 'username' not in login_session:
        return render_template('publicrestaurants.html',
                               restaurant=restaurant)
    else:
        return render_template('restaurants.html',
                           restaurant=restaurant)

# Create a new restaurant
@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    # Check login.
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newRest = Restaurant(name=request.form['name'],
                             user_id=login_session['user_id']
        )
        session.add(newRest)
        session.commit()
        flash(newRest.name + " created!")
        return redirect(url_for('allRestaurants'))
    else:
        return render_template('newrestaurant.html')

# Edit a restaurant
@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if restaurant.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this restaurant.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            restaurant.name = request.form['name']

        session.add(restaurant)
        session.commit()
        flash(restaurant.name + " edited!")
        return redirect(url_for('allRestaurants'))
    else:
        return render_template('editrestaurant.html',
                               restaurant_id=restaurant_id,
                               r=restaurant)

# Delete a restaurant
@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if restaurant.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this restaurant.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        flash(restaurant.name + " deleted!")
        return redirect(url_for('allRestaurants'))
    else:
        return render_template('deleterestaurant.html',
                               r=restaurant,
                               restaurant_id=restaurant_id)


# Show a specific restaurant menu
@app.route('/restaurant/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = (session.query(MenuItem)
             .filter_by(restaurant_id=restaurant.id)
             .order_by(MenuItem.course, MenuItem.name))
    creator = getUserInfo(restaurant.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicmenu.html',
                               items = items,
                               restaurant = restaurant,
                               creator = creator)
    else:
        return render_template('menu.html',
                               items = items,
                               restaurant = restaurant,
                              creator = creator)

# Add a new menu item
@app.route('/restaurant/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'],
                           price='$' + request.form['price'],
                           description=request.form['desc'],
                           course=request.form['course'],
                           restaurant_id=restaurant_id,
                           user_id=resturant.user_id

        )
        session.add(newItem)
        session.commit()
        flash(newItem.name + " created!")
        return redirect(url_for('restaurantMenu',
                                restaurant_id=restaurant_id))
    else:
        rest = session.query(Restaurant).filter_by(id=restaurant_id).one()
        return render_template('newmenuitem.html',
                               restaurant_id=restaurant_id,
                               r=rest)

# Edit a menu item
@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['course']:
            editedItem.course = request.form['course']
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['price']:
            editedItem.price = '$ ' +request.form['price']
        if request.form['desc']:
            editedItem.description = request.form['desc']
        session.add(editedItem)
        session.commit()
        flash(editedItem.name +" edited!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html',
                               restaurant_id=restaurant_id,
                               menu_id=menu_id,
                               i=editedItem,
                              r=restaurant)

# Delete a menu item
@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    deleteItem = session.query(MenuItem).filter_by(id=menu_id).one()
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash(deleteItem.name +" deleted!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html',
                               menu_id=menu_id,
                               i=deleteItem,
                               r=restaurant)


# Make API Endpoint for all items per restaurant (GET)
@app.route('/restaurants/JSON')
def restaurantJSON():
    restaurant = session.query(Restaurant).all()
    return jsonify(Restaurants=[i.serialize for i in restaurant])

# Make API Endpoint for all items per restaurant (GET)
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = (session.query(MenuItem)
             .filter_by(restaurant_id=restaurant_id)
             .all())
    return jsonify(MenuItems=[i.serialize for i in items])

# Make API Endpoint for one item from a restaurant (GET)
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def MenuJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
