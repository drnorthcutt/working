from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)



#Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}

# Show all restaurants
@app.route('/')
@app.route('/restaurants')
def allRestaurants():
    #return "All restaurants"
    return render_template('restaurants.html',
                           restaurants=restaurants)

@app.route('/restaurant/new')
def newRestaurant():
    #return "New Restaurant"
    return render_template('newrestaurant.html',
                           restaurants=restaurants)

@app.route('/restaurant/<int:restaurant_id>/edit')
def editRestaurant(restaurant_id):
    #return "Edit restaurant"
    return render_template('editrestaurant.html',
                           restaurant=restaurant,
                           restaurant_id=restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/delete')
def deleteRestaurant(restaurant_id):
    #return "delete restaurant"
    return render_template('deleterestaurant.html',
                           restaurant=restaurant,
                           restaurant_id=restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    #return "restaurant menu"
    return render_template('menu.html',
                           restaurant=restaurant,
                           items=items,
                           ristaurant_id=restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    return "new menu item"

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/',
           methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    return "edit menu item"

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/',
           methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    return "delete menu item"



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
