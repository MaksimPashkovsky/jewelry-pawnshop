from operator import attrgetter
from flask import Flask, render_template, request, redirect, flash, url_for
from db_setup import session
from models import ProductType, User, Product, CartNote
from flask_login import login_user, current_user, login_required, logout_user, LoginManager
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.secret_key = 'qwerty123'
login_manager = LoginManager(app)

PRODUCT_TYPES = session.query(ProductType).all()


@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(user_id)


@app.route('/')
def main_page():
    return render_template('main_page.html', types=PRODUCT_TYPES)


@app.route('/login', methods=['GET', 'POST'])
def login_page():

    if request.method == 'GET':
        return render_template('login.html')

    login = request.form.get('login')
    password = request.form.get('password')
    user = User.query.filter_by(login=login).first()

    if user is None:
        flash('User not found!')
        return render_template('login.html')

    if check_password_hash(user.password, password):
        login_user(user)
        next_page = request.form.get('next')

        if next_page:
            return redirect(next_page)

        return redirect(url_for('main_page'))

    flash('Wrong password!')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():

    if request.method == 'GET':
        return render_template('register.html')

    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if password != password2:
        flash("Password doesn't match!")
        return render_template('register.html')

    new_user = User(login=login, password=generate_password_hash(password), reg_date=datetime.now())

    session.add(new_user)
    session.commit()

    return redirect(url_for('login_page'))


@app.route('/logout', methods=['GET'])
@login_required
def logout_page():
    logout_user()
    return redirect(url_for('main_page'))


@app.after_request
def redirect_to_sign_in(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)
    return response


@app.route('/catalog/<product_type>', methods=['GET', 'POST'])
def catalog_page(product_type):

    product_type_object = session.query(ProductType)\
        .filter_by(name=product_type.capitalize())\
        .first()

    # All products of concrete type
    all_products = session.query(Product)\
        .filter_by(type=product_type_object.id)\
        .all()

    if len(all_products) == 0:
        min_price, max_price = '', ''
    else:
        min_price = min(all_products, key=attrgetter('price')).price
        max_price = max(all_products, key=attrgetter('price')).price

    if request.method == 'GET':
        return render_template('catalog.html', product_type=product_type, types=PRODUCT_TYPES,
                               products=sorted(all_products, key=attrgetter('name')),
                               min_price=min_price, max_price=max_price)

    price_start = request.form.get('price-start')
    price_end = request.form.get('price-end')

    if price_start == '':
        price_start = min_price

    if price_end == '':
        price_end = max_price

    filtered_products = list(filter(lambda x: float(price_start) <= x.price <= float(price_end), all_products))

    sorting_option = request.form.get('sorting')

    field, order = sorting_option.split('-')
    sorted_products = sorted(filtered_products, key=attrgetter(field), reverse=True if order == 'desc' else False)

    return render_template('catalog.html', product_type=product_type, types=PRODUCT_TYPES, products=sorted_products,
                           min_price=price_start, max_price=price_end, sorting_option=sorting_option)


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    id_ = data['id']
    new_cart_note = CartNote(user_id=current_user.id, product_id=id_)
    session.add(new_cart_note)
    session.commit()
    return "added"


@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    data = request.get_json()
    id_ = data['id']
    note_to_delete = session.query(CartNote).filter_by(user_id=current_user.id, product_id=id_).one()
    session.delete(note_to_delete)
    session.commit()
    return "removed"


@app.route('/confirm', methods=['GET'])
def confirm():
    cart_notes = session.query(CartNote)\
        .filter_by(user_id=current_user.id)\
        .all()

    for note in cart_notes:
        product = session.query(Product).filter_by(id=note.product_id).first()
        product.quantity -= 1
        session.add(product)
        session.commit()

        session.delete(note)
        session.commit()

    return redirect(url_for('main_page'))


@app.route('/cart', methods=['GET'])
@login_required
def cart_page():
    cart_notes = session.query(CartNote)\
        .filter_by(user_id=current_user.id)\
        .all()

    products = [note.product for note in cart_notes]

    return render_template('cart.html', types=PRODUCT_TYPES, products=products)
