import sys
from datetime import datetime
from collections import Counter
from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from . import cart
from ..email import mail_service
from ..models import History
from app import storage


@cart.route('/', methods=['GET'])
@login_required
def cart_page():
    articles = current_user.articles_in_cart
    return render_template('cart.html', articles=articles)


@cart.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    id = data['id']
    article = storage.get_article_by_id(id)
    current_user.articles_in_cart.append(article)
    storage.session.commit()
    return '', 204


@cart.route('/remove/<id>', methods=['GET'])
@login_required
def remove_from_cart(id):
    article = storage.get_article_by_id(id)
    current_user.articles_in_cart.remove(article)
    storage.session.commit()
    flash('Removed from cart')
    return redirect(url_for('.cart_page'))


@cart.route('/remove-all', methods=['GET'])
@login_required
def remove_all_from_cart():
    current_user.articles_in_cart.clear()
    storage.session.commit()
    flash('Removed all')
    return redirect(url_for('.cart_page'))


@cart.route('/confirm', methods=['GET'])
@login_required
def confirm():
    date = datetime.now()
    total_sum = 0
    articles = ''
    articles_in_cart = current_user.articles_in_cart

    for item in articles_in_cart:
        total_sum += item.estimated_price
        articles += str(item) + '\n'

        h = History(date=date)
        h.article = item
        current_user.articles_in_history.append(h)

        item.for_sale = False
        storage.save(item)
        current_user.articles_in_cart.remove(item)
        storage.session.commit()

    cheque_body = 'UVELIRKA JEWELRY PAWNSHOP\n\n'
    cheque_body += f'{date} you bought {len(articles_in_cart)} items, total amount: ${total_sum}\n'
    cheque_body += f'Items:\n'
    cheque_body += articles + '\n\n'
    cheque_body += url_for('main.main_page', _external=True) + '\n'
    cheque_body += 'Thank you!'

    user = storage.get_user_by_id(current_user.user_id)

    account = storage.get_account_by_id(user.account_id)
    account.balance -= total_sum
    storage.save(account)

    mail_service.send_email(current_user.email, 'Your cheque', cheque_body)
    return '', 200
