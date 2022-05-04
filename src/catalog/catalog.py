from operator import attrgetter
from difflib import SequenceMatcher
from flask import Blueprint, request, render_template, session, redirect, url_for
from database_service import DatabaseService

catalog = Blueprint('catalog', __name__, template_folder='templates', static_folder='static')
storage = DatabaseService()


@catalog.route('/<product_type>', methods=['GET', 'POST'])
def catalog_page(product_type):

    product_type_object = storage.get_product_type_by_name(product_type.capitalize())

    # All products of concrete type
    all_products = storage.get_products_by_type(product_type_object.id)

    if request.method == 'GET':
        return render_template('catalog/catalog.html', product_type=product_type,
                               products=sorted(all_products, key=attrgetter('name')))

    search_string = request.form.get('search-string')

    if search_string:
        all_products = list(filter(lambda x: SequenceMatcher(None, search_string, x.name).ratio() >= 0.3, all_products))

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

    return render_template('catalog/catalog.html', product_type=product_type, products=sorted_products,
                           sorting_option=sorting_option)


@catalog.route('/product/<id>')
def product_page(id):
    product = storage.get_product_by_id(id)
    num_of_purchases = len(storage.get_all_history_notes_by_product_id(id))
    return render_template('product.html', product=product, num_of_purchases=num_of_purchases)


@catalog.route('/clear-filters/<product_type>')
def clear_filters(product_type):
    session['price_start'] = ''
    session['price_end'] = ''
    return redirect(url_for('.catalog_page', product_type=product_type))