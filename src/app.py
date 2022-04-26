import random
from datetime import datetime
from operator import attrgetter
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_login import login_user, current_user, login_required, logout_user, LoginManager
from flask_admin.contrib.sqla import ModelView
from flask_toastr import Toastr
from flask_admin import Admin
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from decouple import config
from db_setup import session as db_session
from models import ProductType, User, Product, CartNote
from admin_views import ProductView, Controller


app = Flask(__name__, static_folder='static')
app.secret_key = config('APP_SECRET_KEY')
app.config.from_pyfile('mail_config.cfg')
app.config.from_pyfile('toastr_config.cfg')
app.jinja_env.globals['PRODUCT_TYPES'] = db_session.query(ProductType).all()
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

url_safe_timed_serializer = URLSafeTimedSerializer(config('URL_SAFE_TIMED_SERIALIZER_SECRET_KEY'))
login_manager = LoginManager(app)
toastr = Toastr(app)
mail = Mail(app)
admin = Admin(app)
admin.add_view(Controller(User, db_session))
admin.add_view(ProductView(Product, db_session))
admin.add_view(ModelView(CartNote, db_session))
admin.add_view(ModelView(ProductType, db_session))


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(user_id)


@app.route('/')
def main_page():
    all_products = db_session.query(Product).all()
    random_products = random.sample(all_products, 3)
    return render_template('main_page.html', random_products=random_products)


@app.route('/login', methods=['GET', 'POST'])
def login_page():

    if request.method == 'GET':
        return render_template('login.html')

    login = request.form.get('login')
    password = request.form.get('password')
    user = User.query.filter_by(login=login).first()

    if user is None:
        flash('User not found!', 'error')
        return redirect(url_for('login_page'))

    if check_password_hash(user.password, password):

        if not user.is_verified:
            flash('Account is not verified. Check your email', 'warning')
            return redirect(url_for('login_page'))

        login_user(user)
        next_page = request.form.get('next')

        if user.is_admin:
            return redirect('/admin')

        if next_page:
            return redirect(next_page)

        return redirect(url_for('main_page'))

    flash('Wrong password!', 'error')
    return redirect(url_for('login_page'))


@app.route('/register', methods=['GET', 'POST'])
def register_page():

    if request.method == 'GET':
        return render_template('register.html')

    login = request.form.get('login')
    password = request.form.get('password')
    email = request.form.get('email')
    session['email'] = email

    new_user = User(login=login, password=generate_password_hash(password),
                    email=email, reg_date=datetime.now(), is_verified=False)

    db_session.add(new_user)
    db_session.commit()

    return redirect(url_for('send_email'))


@app.route('/send_email')
def send_email():
    email = session['email']
    token = url_safe_timed_serializer.dumps(email, salt='salt')
    msg = Message('Confirm email!', sender='jewelry-shop@yahoo.com', recipients=[email])
    link = url_for('confirm_email', token=token, _external=True)
    msg.body = 'Your link is: ' + link
    mail.send(msg)
    flash('Email sent')
    return redirect(url_for('login_page'))


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = url_safe_timed_serializer.loads(token, salt='salt', max_age=3600)
    except SignatureExpired:
        return render_template('email_confirm.html', success=False)
    user = db_session.query(User).filter_by(email=email).first()
    user.is_verified = True
    db_session.add(user)
    db_session.commit()
    return render_template('email_confirm.html', success=True)


@app.route('/logout', methods=['GET'])
@login_required
def logout_page():
    logout_user()
    session.clear()
    return redirect(url_for('main_page'))


@app.after_request
def redirect_to_sign_in(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)
    return response


@app.route('/catalog/<product_type>', methods=['GET', 'POST'])
def catalog_page(product_type):

    product_type_object = db_session.query(ProductType)\
        .filter_by(name=product_type.capitalize())\
        .first()

    # All products of concrete type
    all_products = db_session.query(Product)\
        .filter_by(type=product_type_object.id)\
        .all()

    if request.method == 'GET':
        return render_template('catalog.html', product_type=product_type,
                               products=sorted(all_products, key=attrgetter('name')))

    price_start = request.form.get('price-start')
    price_end = request.form.get('price-end')

    if price_start == '' and all_products:
        price_start = min(all_products, key=attrgetter('price')).price

    if price_end == '' and all_products:
        price_end = max(all_products, key=attrgetter('price')).price

    filtered_products = list(filter(lambda x: float(price_start) <= x.price <= float(price_end), all_products))

    session['price_start'] = price_start
    session['price_end'] = price_end

    sorting_option = request.form.get('sorting')

    field, order = sorting_option.split('-')
    sorted_products = sorted(filtered_products, key=attrgetter(field), reverse=order == 'desc')

    return render_template('catalog.html', product_type=product_type, products=sorted_products,
                           sorting_option=sorting_option)


@app.route('/catalog/product/<id>')
def product_page(id):
    product = db_session.query(Product).filter_by(id=id).first()
    return render_template('product.html', product=product)


@app.route('/clear-filters/<product_type>')
def clear_filters(product_type):
    session['price_start'] = ''
    session['price_end'] = ''
    return redirect(url_for('catalog_page', product_type=product_type))


@app.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    id = data['id']
    new_cart_note = CartNote(user_id=current_user.id, product_id=id)
    db_session.add(new_cart_note)
    db_session.commit()
    return '', 204


@app.route('/remove-from-cart/<id>', methods=['GET'])
@login_required
def remove_from_cart(id):
    note_to_delete = db_session.query(CartNote)\
        .filter_by(user_id=current_user.id, product_id=id)\
        .first()
    db_session.delete(note_to_delete)
    db_session.commit()
    flash('Removed from cart')
    return redirect(url_for('cart_page'))


@app.route('/remove-all-from-cart', methods=['GET'])
def remove_all_from_cart():
    db_session.query(CartNote).filter_by(user_id=current_user.id).delete(synchronize_session='fetch')
    db_session.commit()
    flash('Removed all')
    return redirect(url_for('cart_page'))


@app.route('/confirm', methods=['GET'])
@login_required
def confirm():
    cart_notes = db_session.query(CartNote)\
        .filter_by(user_id=current_user.id)\
        .all()

    for note in cart_notes:
        product = db_session.query(Product).filter_by(id=note.product_id).first()
        product.quantity -= 1
        db_session.add(product)
        db_session.commit()
        db_session.delete(note)
        db_session.commit()

    return redirect(url_for('main_page'))


@app.route('/cart', methods=['GET'])
@login_required
def cart_page():
    cart_notes = db_session.query(CartNote)\
        .filter_by(user_id=current_user.id)\
        .all()

    products = [note.product for note in cart_notes]

    return render_template('cart.html', products=products)
