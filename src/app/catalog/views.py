import sys
from flask import request, render_template, session, redirect, url_for
from . import catalog
from app import storage
import math


@catalog.route('/', methods=['GET', 'POST'])
def catalog_page():
    for a_type in ['ring', 'bracelet', 'watch', 'necklace', 'pendant', 'chain', 'earrings', 'brooch']:
        session['match-' + a_type] = ''

    for sort in ['name-asc', 'name-desc', 'estimated_price-asc', 'estimated_price-desc']:
        session['sort-' + sort] = ''

    session['search-string'] = ''

    session['price-start'] = ''
    session['price-end'] = ''

    sorting_option = ""

    if request.method == "POST":
        sorting_option = request.form.get('sorting-input')
        session['sort-' + sorting_option] = 'selected'

    if request.args.get('sort'):
        sorting_option = request.args.get('sort')

    if not sorting_option:
        sorting_option = "name-asc"

    field, order = sorting_option.split('-')

    articles_per_page = 12
    page = request.args.get('page', 1, type=int)
    offset = articles_per_page * (page - 1)

    filtered_types = []

    if request.method == 'POST':
        for a_type in [t.name.lower() for t in storage.get_all_article_types()]:
            if request.form.get('match-{}'.format(a_type)):
                session['match-{}'.format(a_type)] = 'checked'
                filtered_types.append(a_type.capitalize())

    if request.args.get('types'):
        filtered_types = request.args.get('types').split(',')

    if not filtered_types:
        filtered_types = [t.name for t in storage.get_all_article_types()]

    search_string = ''

    if request.method == 'POST':
        search_string = request.form.get('search-string')
        session['search-string'] = search_string

    if request.args.get('search'):
        search_string = request.args.get('search')

    price_start, price_end = 0, 0

    if request.method == 'POST':
        price_start = request.form.get('price-start')
        price_end = request.form.get('price-end')
        session['price-start'] = price_start
        session['price-end'] = price_end

    if request.args.get('price-start'):
        price_start = request.args.get('price-start')

    if request.args.get('price-end'):
        price_end = request.args.get('price-end')

    if not price_start:
        price_start = storage.get_articles_for_sale_min_price(filtered_types, search_string)
        session['price-start'] = price_start
        print('price_start = ', price_start, file=sys.stderr)

    if not price_end:
        price_end = storage.get_articles_for_sale_max_price(filtered_types, search_string)
        session['price-end'] = price_end
        print('price_end = ', price_end, file=sys.stderr)

    def update_query_param(name, value):
        base, *params = request.url.split('?')
        params = dict(el.split('=') for el in params[0].split('&')) if params else dict()
        params[name] = value
        params['types'] = ",".join(filtered_types)
        params['sort'] = sorting_option
        params['search'] = search_string
        params['price-start'] = price_start
        params['price-end'] = price_end
        return base + '?' + "&".join(f"{p}={v}" for p, v in params.items())

    articles_on_page = storage.get_articles_for_sale(offset, articles_per_page, field, 1 if order == 'desc' else 0, filtered_types, search_string, price_start, price_end)

    total_pages = math.ceil(storage.get_articles_for_sale_count(filtered_types, search_string, price_start, price_end) / articles_per_page)

    return render_template('catalog.html', articles=articles_on_page, current_page=page,
                           total_pages=total_pages, update_query_param=update_query_param)


@catalog.route('/article/<int:id>')
def article_page(id):
    article = storage.get_article_by_id(id)
    return render_template('article.html', article=article)


@catalog.route('/clear-filters/<article_type>')
def clear_filters(article_type):
    session['price_start'] = ''
    session['price_end'] = ''
    return redirect(url_for('.catalog_page', article_type=article_type))
