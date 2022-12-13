from datetime import datetime
from collections import Counter
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from database_service import DatabaseService
from models import CartNote, HistoryNote
from email_ import mail_service

cart = Blueprint('cart', __name__, template_folder='templates', static_folder='static')
storage = DatabaseService()


@cart.route('/', methods=['GET'])
@login_required
def cart_page():
    cart_notes = storage.get_cart_notes_by_user_id(current_user.user_id)
    articles = [note.article for note in cart_notes]
    return render_template('cart/cart.html', articles=articles)


@cart.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    id = data['id']
    new_cart_note = CartNote(user_id=current_user.user_id, article_id=id)
    storage.save(new_cart_note)
    return '', 204


@cart.route('/remove/<id>', methods=['GET'])
@login_required
def remove_from_cart(id):
    note_to_delete = storage.get_cart_note(current_user.user_id, id)
    storage.delete(note_to_delete)
    flash('Removed from cart')
    return redirect(url_for('.cart_page'))


@cart.route('/remove-all', methods=['GET'])
@login_required
def remove_all_from_cart():
    storage.delete_cart_notes_by_user_id(current_user.user_id)
    flash('Removed all')
    return redirect(url_for('.cart_page'))


@cart.route('/confirm', methods=['GET'])
@login_required
def confirm():
    date = datetime.now()
    total_sum = 0
    articles = ''
    cart_notes = storage.get_cart_notes_by_user_id(current_user.user_id)

    quantities = Counter([note.article_id for note in cart_notes])

    for k, v in quantities.items():
        article = storage.get_article_by_id(k)
        if article.quantity < v:
            return '', 500

    for note in cart_notes:
        article = storage.get_article_by_id(note.article_id)
        total_sum += article.estimated_price
        article.quantity -= 1
        articles += str(article) + '\n'
        storage.save(HistoryNote(user_id=current_user.user_id, article_id=article.article_id, date=date))
        storage.save(article)
        storage.delete(note)

    cheque_body = 'UVELIRKA JEWELRY PAWNSHOP\n\n'
    cheque_body += f'{date} you bought {len(cart_notes)} items, total amount: ${total_sum}\n'
    cheque_body += f'Items:\n'
    cheque_body += articles + '\n\n'
    cheque_body += url_for('main_page', _external=True) + '\n'
    cheque_body += 'Thank you!'

    user = storage.get_user_by_id(current_user.user_id)

    account = storage.get_account_by_id(user.account_id)
    account.balance -= total_sum
    storage.save(account)

    mail_service.send_email(current_user.email, 'Your cheque', cheque_body)
    return '', 200
