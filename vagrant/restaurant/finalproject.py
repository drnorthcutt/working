from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

from restaurant_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Show all restaurants
@app.route('/')
@app.route('/restaurants')
def allRestaurants():
    #return "All restaurants alphabetical"
    restaurant = session.query(Restaurant).order_by(Restaurant.name).all()
    return render_template('restaurants.html',
                           restaurant=restaurant)

@app.route('/restaurant/new', methods=['GET','POST'])
def newRestaurant():
    #return "New Restaurant"
    if request.method == 'POST':
        newRest = Restaurant(
                        name=request.form['name'],
        )
        session.add(newRest)
        session.commit()
        flash(newRest.name +" created!")
        return redirect(url_for('allRestaurants'))
    else:
        return render_template('newrestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET','POST'])
def editRestaurant(restaurant_id):
    #return "Edit restaurant"
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            restaurant.name = request.form['name']

        session.add(restaurant)
        session.commit()
        flash(restaurant.name +" edited!")
        return redirect(url_for('allRestaurants'))
    else:
        return render_template('editrestaurant.html',
                               restaurant_id=restaurant_id,
                               r=restaurant)

@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    #return "delete restaurant"
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        flash(restaurant.name +" deleted!")
        return redirect(url_for('allRestaurants'))
    else:
        return render_template('deleterestaurant.html',
                               r=restaurant,
                               restaurant_id=restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    #return "restaurant menu"
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = (session.query(MenuItem)
             .filter_by(restaurant_id=restaurant.id)
             .order_by(MenuItem.course,MenuItem.name))
    sides = (session.query(MenuItem)
             .filter_by(restaurant_id=restaurant.id, course='Side'))
    entrees = (session.query(MenuItem)
               .filter_by(restaurant_id=restaurant.id, course='Entree').first())
    return render_template('menu.html',
                           restaurant=restaurant,
                           items=items,
                            sides=sides,
                           entrees=entrees)

@app.route('/restaurant/<int:restaurant_id>/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    #return "new menu item"
    if request.method == 'POST':
        newItem = MenuItem(
                            name=request.form['name'],
                            price='$' +request.form['price'],
                            description=request.form['desc'],
                            course=request.form['course'],
                            restaurant_id=restaurant_id
        )
        session.add(newItem)
        session.commit()
        flash(newItem.name +" created!")
        return redirect(url_for('restaurantMenu',
                                restaurant_id=restaurant_id))
    else:
        rest = session.query(Restaurant).filter_by(id = restaurant_id).one()
        return render_template('newmenuitem.html',
                               restaurant_id=restaurant_id,
                               r=rest)

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/',
           methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    #return "edit menu item"
    return render_template('editmenuitem.html',
                           restaurant=restaurant,
                           item=item,
                           restaurant_id=restaurant_id,
                           menu_id=menu_id)

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/',
           methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    #return "delete menu item"
    return render_template('deletemenuitem.html',
                           restaurant=restaurant,
                           item=item,
                           restaurant_id=restaurant_id,
                           menu_id=menu_id)

# Make API Endpoint for all items per restaurant (GET)
@app.route('/restaurants/JSON')
def restaurantJSON():
    restaurant = session.query(Restaurant).all()
    return jsonify(Restaurants=[i.serialize for i in restaurant])

# Make API Endpoint for all items per restaurant (GET)
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


# Make API Endpoint for one item from a restaurant (GET)
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def MenuJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=item.serialize)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
