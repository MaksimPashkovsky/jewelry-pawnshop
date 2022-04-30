import random
from datetime import datetime
from operator import attrgetter
from collections import defaultdict
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
    return redirect(url_for('send_email'))


@app.route('/send_email')
def send_email():
    email = session['email']
    token = mail_service.generate_token(email)
    body = 'Your link is: ' + url_for('confirm_email', token=token, _external=True)
    mail_service.send_email(email, body)
    flash('Email sent', 'success')
    return redirect(url_for('login_page'))


@app.route('/confirm_email/<token>')
def confirm_email(token):
    email = mail_service.retrieve_email(token)
    if not email:
        return render_template('email_confirm.html', success=False)
    user = storage.get_user_by_email(email)
    user.is_verified = True
    storage.save(user)
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

    product_type_object = storage.get_product_type_by_name(product_type.capitalize())

    # All products of concrete type
    all_products = storage.get_products_by_type(product_type_object.id)

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
    product = storage.get_product_by_id(id)
    num_of_purchases = len(storage.get_all_history_notes_by_product_id(id))
    return render_template('product.html', product=product, num_of_purchases=num_of_purchases)


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
    cart_notes = storage.get_cart_notes_by_user_id(current_user.id)
    for note in cart_notes:
        product = storage.get_product_by_id(note.product_id)
        total_sum += product.price
        product.quantity -= 1
        history_note = HistoryNote(user_id=current_user.id, product_id=product.id, date=date)
        storage.save(history_note)
        storage.save(product)
        storage.delete(note)

    user = storage.get_user_by_id(current_user.id)
    user.balance -= total_sum
    storage.save(user)
    return '', 200


@app.route('/cart', methods=['GET'])
@login_required
def cart_page():
    cart_notes = storage.get_cart_notes_by_user_id(current_user.id)
    products = [note.product for note in cart_notes]
    return render_template('cart.html', products=products)


@app.route('/profile', methods=['GET'])
@login_required
def profile_page():
    return render_template('profile.html')


@app.route('/profile/save', methods=['POST'])
def save_profile_info():
    data = request.get_json()
    field, value = tuple(data.items())[0]

    if field != 'balance' and value in storage.get_user_column(field):
        return '', 500

    user = storage.get_user_by_id(current_user.id)
    setattr(user, field, value)
    storage.save(user)
    return '', 200


@app.route('/profile/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    old_password = data['old_password']
    new_password = data['new_password']

    user = storage.get_user_by_id(current_user.id)

    if check_password_hash(user.password, old_password):
        user.password = generate_password_hash(new_password)
        storage.save(user)
        return '', 200
    return '', 500


@app.route('/history', methods=['GET'])
def history_page():
    history_notes = storage.get_all_history_notes_by_user_id(current_user.id)
    d = [(note.date, note) for note in history_notes]
    res = defaultdict(list)
    for k, v in d:
        res[k].append(v)
    final = [{'date': k, 'items': v} for k, v in res.items()]
    final.sort(key=lambda x: x['date'], reverse=True)
    return render_template('history.html', notes=final)