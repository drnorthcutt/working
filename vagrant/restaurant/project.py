from flask import Flask, render_template, url_for, request, redirect
app = Flask(__name__)

from restaurant_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/restaurant/<int:restaurant_id>/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(
                            name=request.form['name'],
                            price='$' +request.form['price'],
                            description=request.form['desc'],
                            restaurant_id=restaurant_id
        )
        session.add(newItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        rest = session.query(Restaurant).filter_by(id = restaurant_id).one()
        return render_template('newmenuitem.html',
                               restaurant_id=restaurant_id,
                               r=rest)


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['price']:
            editedItem.price = '$ ' +request.form['price']
        if request.form['desc']:
            editedItem.description = request.form['desc']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html',
                               restaurant_id=restaurant_id,
                               menu_id=menu_id,
                               i=editedItem,
                              r=restaurant)


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    deleteItem = session.query(MenuItem).filter_by(id=menu_id).one()
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html',
                               menu_id=menu_id,
                               i=deleteItem,
                               r=restaurant)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
