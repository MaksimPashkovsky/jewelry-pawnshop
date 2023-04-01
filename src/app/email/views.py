from flask import session, url_for, flash, redirect, render_template
from . import email, mail_service
from app import storage


@email.route('/send')
def send_email():
    email = session['email']
    token = mail_service.generate_token(email)
    body = 'Your link is: ' + url_for('.confirm_email', token=token, _external=True)
    mail_service.send_email(email, 'Confirm email!', body)
    flash('Email sent! The link will be valid for 1 hour', 'success')
    return redirect(url_for('login_page'))


@email.route('/confirm/<token>')
def confirm_email(token):
    email = mail_service.retrieve_email(token)
    if not email:
        return render_template('email/email_confirm.html', success=False)
    user = storage.get_user_by_email(email)
    user.is_verified = True
    storage.save(user)
    return render_template('email/email_confirm.html', success=True)