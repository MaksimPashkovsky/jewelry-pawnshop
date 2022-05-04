import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_login import login_user, login_required, logout_user, LoginManager
from flask_toastr import Toastr
from flask_admin import Admin
from flask_mail import Mail
from werkzeug.security import check_password_hash, generate_password_hash
from decouple import config
from models import ProductType, User, Product, CartNote, HistoryNote
from admin_views import *
from database_service import DatabaseService
import mail_service
from profile.profile import profile
from email_.email import email
from catalog.catalog import catalog
from cart.cart import cart

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
admin.add_view(CartNoteView(CartNote, storage.session))
admin.add_view(ProductTypeView(ProductType, storage.session))
admin.add_view(HistoryNoteView(HistoryNote, storage.session))

app.register_blueprint(profile, url_prefix='/profile')
app.register_blueprint(email, url_prefix='/email')
app.register_blueprint(catalog, url_prefix='/catalog')
app.register_blueprint(cart, url_prefix='/cart')


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
