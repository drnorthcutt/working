from flask import Flask, render_template, url_for, request, redirect, flash
from flask import jsonify
from restaurant_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# For OAuth
from flask import session as login_session
import random, string

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
    return render_template('login.html')


# Show all restaurants
@app.route('/')
@app.route('/restaurants')
def allRestaurants():
    # return "All restaurants alphabetical"
    restaurant = session.query(Restaurant).order_by(Restaurant.name).all()
    return render_template('restaurants.html',
                           restaurant=restaurant)

# Create a new restaurant
@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    # return "New Restaurant"
    if request.method == 'POST':
        newRest = Restaurant(
                        name=request.form['name'],
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
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
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
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
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
    sides = (session.query(MenuItem)
             .filter_by(restaurant_id=restaurant.id, course='Side'))
    entrees = (session.query(MenuItem)
               .filter_by(restaurant_id=restaurant.id, course='Entree')
               .first())
    return render_template('menu.html',
                           restaurant=restaurant,
                           items=items,
                           sides=sides,
                           entrees=entrees)

# Add a new menu item
@app.route('/restaurant/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(
                            name=request.form['name'],
                            price='$' + request.form['price'],
                            description=request.form['desc'],
                            course=request.form['course'],
                            restaurant_id=restaurant_id
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
