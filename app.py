from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "secret_key"

import sqlite3

# Path to the SQLite database
DATABASE = 'database/tastytaps.db'


def connect_db():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Optional: Access rows as dictionaries
    return conn

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Routes
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    # Fetch the search query if provided
    search_query = request.args.get('search', '').strip()

    # Get the dishes based on the search query
    conn = connect_db()
    cursor = conn.cursor()

    if search_query:
        cursor.execute(
            "SELECT * FROM dishes WHERE name LIKE ? OR categories LIKE ?",
            (f"%{search_query}%", f"%{search_query}%")
        )
    else:
        cursor.execute("SELECT * FROM dishes")

    dishes = cursor.fetchall()
    conn.close()

    # Ensure the cart is a dictionary
    cart = session.get('cart', {})

    # Calculate total price if cart is a dictionary
    total_price = 0
    if isinstance(cart, dict):
        total_price = sum(item['price'] * item['quantity'] for item in cart.values())

    return render_template('menu.html', dishes=dishes, cart=cart, total_price=total_price)




def get_dishes_by_category(categories):
    """Fetch dishes by a specific category."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = "SELECT * FROM dishes WHERE categories LIKE ?"
        cursor.execute(query, (f"%{categories}%",))
        dishes = cursor.fetchall()
    finally:
        conn.close()
    return dishes


@app.route('/menu/breakfast')
def breakfast():
    # Fetch dishes from the database for South Indian category
    dishes = get_dishes_by_category('Breakfast')
    return render_template('menu.html', category='Breakfast', dishes=dishes)

@app.route('/menu/breads')
def breads():
    # Fetch dishes from the database for North Indian category
    dishes = get_dishes_by_category('Breads')
    return render_template('menu.html', category='Breads', dishes=dishes)

@app.route('/menu/starters')
def starters():
    # Fetch dishes from the database for Chinese category
    dishes = get_dishes_by_category('Starters')
    return render_template('menu.html', category='Starters', dishes=dishes)

@app.route('/menu/main_course')
def main_course():
    # Fetch dishes from the database for Italian category
    dishes = get_dishes_by_category('Main Course')
    return render_template('menu.html', category='Main Course', dishes=dishes)

@app.route('/menu/rice')
def rice():
    # Fetch dishes from the database for Dessert category
    dishes = get_dishes_by_category('Rice')
    return render_template('menu.html', category='Rice', dishes=dishes)

@app.route('/menu/noodles')
def noodles():
    # Fetch dishes from the database for Beverages category
    dishes = get_dishes_by_category('Noodles')
    return render_template('menu.html', category='Noodles', dishes=dishes)

@app.route('/menu/pizza')
def pizza():
    # Fetch dishes from the database for Beverages category
    dishes = get_dishes_by_category('Pizza')
    return render_template('menu.html', category='Pizza', dishes=dishes)

@app.route('/menu/burger')
def burger():
    # Fetch dishes from the database for Beverages category
    dishes = get_dishes_by_category('Burger')
    return render_template('menu.html', category='Burger', dishes=dishes)

@app.route('/menu/pasta')
def pasta():
    # Fetch dishes from the database for Beverages category
    dishes = get_dishes_by_category('Pasta')
    return render_template('menu.html', category='Pasta', dishes=dishes)

@app.route('/menu/snacks')
def snacks():
    # Fetch dishes from the database for Beverages category
    dishes = get_dishes_by_category('Snacks')
    return render_template('menu.html', category='Snacks', dishes=dishes)

@app.route('/menu/chaats')
def chaats():
    # Fetch dishes from the database for Beverages category
    dishes = get_dishes_by_category('Chaats')
    return render_template('menu.html', category='Chaats', dishes=dishes)

@app.route('/menu/dessert')
def dessert():
    # Fetch dishes from the database for Dessert category
    dishes = get_dishes_by_category('Dessert')
    return render_template('menu.html', category='Dessert', dishes=dishes)

@app.route('/menu/beverages')
def beverages():
    # Fetch dishes from the database for Beverages category
    dishes = get_dishes_by_category('Beverages')
    return render_template('menu.html', category='Beverages', dishes=dishes)

@app.before_request
def initialize_cart():
    if 'cart' not in session:
        session['cart'] = {}



@app.route('/add_to_cart/<int:dish_id>', methods=['POST'])
def add_to_cart(dish_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dishes WHERE id = ?", (dish_id,))
    dish = cursor.fetchone()
    conn.close()

    if dish:
        cart = session.get('cart', {})
        if str(dish_id) not in cart:
            cart[str(dish_id)] = {'name': dish[1], 'price': dish[2], 'quantity': 1}
        else:
            cart[str(dish_id)]['quantity'] += 1

        session['cart'] = cart
    return redirect(url_for('menu'))


@app.route('/remove_from_cart/<int:dish_id>')
def remove_from_cart(dish_id):
    cart = session.get('cart', {})
    if str(dish_id) in cart:
        del cart[str(dish_id)]
        session['cart'] = cart
    return redirect(url_for('menu'))


@app.route('/place_order', methods=['POST'])
def place_order():
    cart = session.get('cart', {})

    if cart:
        session['cart'] = {}  # Clear the cart after placing the order
        flash("Order placed successfully!")
    else:
        flash("Your cart is empty. Please add items before placing an order.")

    return redirect('/menu')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    search_query = request.args.get('search', '').strip()  # Default to an empty string if no search query is provided
    dishes = []

    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form['action']
        name = request.form.get('name')
        price = request.form.get('price', type=float)
        dish_id = request.form.get('id', type=int)
        category = request.form.get('category')

        if action == 'add' and name and price and category:
            cursor.execute("INSERT INTO dishes (name, price, categories) VALUES (?, ?, ?)", (name, price, category))
        elif action == 'edit' and dish_id and name and price and category:
            cursor.execute("UPDATE dishes SET name = ?, price = ?, categories = ? WHERE id = ?", (name, price, category, dish_id))
        elif action == 'delete' and dish_id:
            cursor.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
        conn.commit()



    if search_query:
            cursor.execute(
                "SELECT * FROM dishes WHERE name LIKE ? OR categories LIKE ?",
                (f"%{search_query}%", f"%{search_query}%")
            )
    else:
        cursor.execute("SELECT * FROM dishes")

    dishes = cursor.fetchall()
    conn.close()
    return render_template('admin.html', dishes=dishes)



@app.route('/add_dish', methods=['POST'])
def add_dish():
    name = request.form.get('name')
    price = request.form.get('price')
    image = request.files.get('image')
    categories = request.form.get('categories')

    # Ensure fields are filled
    if not name or not price or not categories:
        return "Dish name, price and categories are required!", 400

    # Handle file upload
    filename = None
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Save to database
    with connect_db() as db:
        db.execute(
            'INSERT INTO dishes (name, price, image) VALUES (?, ?, ?)',
            (name, float(price), filename)
        )
        db.commit()

    return redirect('/admin')



@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
