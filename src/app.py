import random
from datetime import datetime
from collections import Counter
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_login import login_user, current_user, login_required, logout_user, LoginManager
from flask_admin.contrib.sqla import ModelView
from flask_toastr import Toastr
from flask_admin import Admin
from flask_mail import Mail
from werkzeug.security import check_password_hash, generate_password_hash
from decouple import config
from models import ProductType, User, Product, CartNote, HistoryNote
from admin_views import ProductView, Controller
from database_service import DatabaseService
import mail_service
from profile.profile import profile
from email_.email import email
from catalog.catalog import catalog

storage = DatabaseService()

app = Flask(__name__, static_folder='static')
app.secret_key = config('APP_SECRET_KEY')
app.config.from_pyfile('mail_config.cfg')
app.config.from_pyfile('toastr_config.cfg')
app.jinja_env.globals['PRODUCT_TYPES'] = storage.get_all_product_types()

login_manager = LoginManager(app)
toastr = Toastr(app)
mail_service.mail = Mail(app)
admin = Admin(app)
admin.add_view(Controller(User, storage.session))
admin.add_view(ProductView(Product, storage.session))
admin.add_view(ModelView(CartNote, storage.session))
admin.add_view(ModelView(ProductType, storage.session))

app.register_blueprint(profile, url_prefix='/profile')
app.register_blueprint(email, url_prefix='/email')
app.register_blueprint(catalog, url_prefix='/catalog')


@login_manager.user_loader
def load_user(user_id):
    return storage.get_user_by_id(user_id)


@app.route('/')
def main_page():
    all_products = storage.get_all_products()
    random_products = random.sample(all_products, 3)
    return render_template('main_page.html', random_products=random_products)


@app.route('/login', methods=['GET', 'POST'])
def login_page():

    if request.method == 'GET':
        return render_template('login.html')

    login = request.form.get('login')
    password = request.form.get('password')
    user = storage.get_user_by_login(login)

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
            return redirect('/admin/')
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

    if login in storage.get_all_logins():
        flash('Such login already in use!', 'error')
        return redirect(url_for('register_page'))

    if email in storage.get_all_emails():
        flash('Such email already in use!', 'error')
        return redirect(url_for('register_page'))

    session['email'] = email

    new_user = User(login=login, password=generate_password_hash(password),
                    email=email, reg_date=datetime.now(), is_verified=False, is_admin=False)

    storage.save(new_user)
    return redirect(url_for('email.send_email'))


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


@app.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    id = data['id']
    new_cart_note = CartNote(user_id=current_user.id, product_id=id)
    storage.save(new_cart_note)
    return '', 204


@app.route('/remove-from-cart/<id>', methods=['GET'])
@login_required
def remove_from_cart(id):
    note_to_delete = storage.get_cart_note(current_user.id, id)
    storage.delete(note_to_delete)
    flash('Removed from cart')
    return redirect(url_for('cart_page'))


@app.route('/remove-all-from-cart', methods=['GET'])
def remove_all_from_cart():
    storage.delete_cart_notes_by_user_id(current_user.id)
    flash('Removed all')
    return redirect(url_for('cart_page'))


@app.route('/confirm', methods=['GET'])
@login_required
def confirm():
    date = datetime.now()
    total_sum = 0
    products = ''
    cart_notes = storage.get_cart_notes_by_user_id(current_user.id)

    quantities = Counter([note.product_id for note in cart_notes])

    for k, v in quantities.items():
        product = storage.get_product_by_id(k)
        if product.quantity < v:
            return '', 500

    for note in cart_notes:
        product = storage.get_product_by_id(note.product_id)
        total_sum += product.price
        product.quantity -= 1
        products += str(product) + '\n'
        storage.save(HistoryNote(user_id=current_user.id, product_id=product.id, date=date))
        storage.save(product)
        storage.delete(note)

    cheque_body = 'UVELIRKA JEWELRY SHOP\n\n'
    cheque_body += f'{date} you bought {len(cart_notes)} items, total amount: ${total_sum}\n'
    cheque_body += f'Items:\n'
    cheque_body += products + '\n\n'
    cheque_body += url_for('main_page', _external=True) + '\n'
    cheque_body += 'Thank you!'

    user = storage.get_user_by_id(current_user.id)
    user.balance -= total_sum
    storage.save(user)
    mail_service.send_email(current_user.email, 'Your cheque', cheque_body)
    return '', 200


@app.route('/cart', methods=['GET'])
@login_required
def cart_page():
    cart_notes = storage.get_cart_notes_by_user_id(current_user.id)
    products = [note.product for note in cart_notes]
    return render_template('cart.html', products=products)
