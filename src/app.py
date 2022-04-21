from flask import Flask, render_template, request, redirect, flash, url_for
from db_setup import session
from models import ProductType, User
from flask_login import login_user, current_user, login_required, logout_user, LoginManager
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from transliterate import translit

app = Flask(__name__, static_folder='static')
app.secret_key = 'qwerty123'
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(user_id)


@app.route('/')
def main_page():
    types = session.query(ProductType).all()
    return render_template('main_page.html', types=types, translit=translit)


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