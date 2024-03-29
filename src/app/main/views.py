from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask import render_template, request, flash, redirect, url_for, session, send_file
from flask_login import login_user, login_required, logout_user
from . import main
from app import storage
from app.models import User, Customer, EstimationOrder
from io import BytesIO
import magic


@main.route('/')
def main_page():
    return render_template('main_page.html')


@main.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')

    login = request.form.get('login')
    password = request.form.get('password')
    user = storage.get_user_by_login(login)

    if user is None:
        flash('User not found!', 'error')
        return redirect(url_for('main.login_page'))

    if check_password_hash(user.password, password):
        if not user.is_verified:
            flash('Account is not verified. Check your email', 'warning')
            return redirect(url_for('main.login_page'))

        login_user(user)
        next_page = request.form.get('next')

        if storage.is_user_admin(user):
            return redirect('/admin/')

        if next_page:
            return redirect(next_page)

        return redirect(url_for('main.main_page'))
    flash('Wrong password!', 'error')
    return redirect(url_for('main.login_page'))


@main.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'GET':
        return render_template('register.html')

    login = request.form.get('login')
    password = request.form.get('password')
    email = request.form.get('email')

    if login in storage.get_all_logins():
        flash('Such login already in use!', 'error')
        return redirect(url_for('main.register_page'))

    if email in storage.get_all_emails():
        flash('Such email already in use!', 'error')
        return redirect(url_for('main.register_page'))

    session['email'] = email

    new_user = User(login=login, password=generate_password_hash(password),
                    email=email, reg_date=datetime.now(), is_verified=False)
    storage.save(new_user)

    new_customer = Customer(user_id=new_user.user_id)
    storage.save(new_customer)

    return redirect(url_for('email.send_email'))


@main.route('/getimage/order/<int:order_id>/<int:file_num>', methods=['GET'])
def getimage(order_id, file_num):

    order = storage.get_estimation_order_by_id(order_id)
    image_content = order.images[file_num]
    mime = magic.from_buffer(image_content, mime=True)

    return send_file(
        BytesIO(image_content),
        mimetype=mime,
        download_name=f"{file_num}.{mime.split(r'/')[-1]}",
        as_attachment=True)


@main.route('/estimation', methods=['POST'])
def estimation():
    name = request.form.get('name')
    phone_number = request.form.get('phone')
    description = request.form.get('description')
    files = list(request.files.getlist('images'))

    if not files:
        flash('Error uploading files', 'error')
        return redirect(url_for('main.main_page'))

    images = [f.read() for f in files]

    o = EstimationOrder(name, phone_number, description, images)
    storage.save(o)

    flash('Thank you!', 'success')
    return redirect(url_for('main.main_page'))


@main.route('/logout', methods=['GET'])
@login_required
def logout_page():
    logout_user()
    session.clear()
    return redirect(url_for('main.main_page'))


@main.after_request
def redirect_to_sign_in(response):
    if response.status_code == 401:
        return redirect(url_for('main.login_page') + '?next=' + request.url)
    return response
