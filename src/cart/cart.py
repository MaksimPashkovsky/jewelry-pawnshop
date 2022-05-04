from datetime import datetime
from collections import Counter
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from database_service import DatabaseService
from models import CartNote, HistoryNote
import mail_service

cart = Blueprint('cart', __name__, template_folder='templates', static_folder='static')
storage = DatabaseService()


@cart.route('/', methods=['GET'])
@login_required
def cart_page():
    cart_notes = storage.get_cart_notes_by_user_id(current_user.id)
    products = [note.product for note in cart_notes]
    return render_template('cart/cart.html', products=products)


@cart.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    id = data['id']
    new_cart_note = CartNote(user_id=current_user.id, product_id=id)
    storage.save(new_cart_note)
    return '', 204


@cart.route('/remove/<id>', methods=['GET'])
@login_required
def remove_from_cart(id):
    note_to_delete = storage.get_cart_note(current_user.id, id)
    storage.delete(note_to_delete)
    flash('Removed from cart')
    return redirect(url_for('.cart_page'))


@cart.route('/remove-all', methods=['GET'])
@login_required
def remove_all_from_cart():
    storage.delete_cart_notes_by_user_id(current_user.id)
    flash('Removed all')
    return redirect(url_for('.cart_page'))


@cart.route('/confirm', methods=['GET'])
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