import sys
from operator import attrgetter
from flask import request, render_template, session, redirect, url_for
from . import catalog
from app import storage
import math


@catalog.route('/', methods=['GET', 'POST'])
def catalog_page():
    for a_type in ['ring', 'bracelet', 'watch', 'necklace', 'pendant', 'chain', 'earrings', 'brooch']:
        session['match-' + a_type] = ''

    if request.method == 'GET':
        articles_per_page = 12
        page = request.args.get('page', 1, type=int)
        offset = articles_per_page * (page - 1)
        articles = storage.get_articles_for_sale(offset, articles_per_page)
        total_pages = math.ceil(storage.get_articles_for_sale_count() / articles_per_page)
        print('total_pages = ', total_pages, file=sys.stderr)
        return render_template('catalog.html', articles=sorted(articles, key=attrgetter('name')), current_page=page,
                               total_pages=total_pages)

    articles = list()

    for a_type in ['ring', 'bracelet', 'watch', 'necklace', 'pendant', 'chain', 'earrings', 'brooch']:
        if request.form.get('match-' + a_type):
            articles.extend(storage.get_article_type_by_name(a_type.capitalize()).articles)
            session['match-' + a_type] = 'checked'

    price_start = request.form.get('price-start')
    price_end = request.form.get('price-end')

    filtered_articles = list(filter(lambda x: float(price_start) <= x.estimated_price <= float(price_end), articles))

    # sorting_option = request.form.get('sorting')

    # if sorting_option == 'num-of-purchased':
    #    sorted_articles = sorted(filtered_articles, key=lambda x: len(x.users_have_in_history), reverse=True)
    # else:
    #    field, order = sorting_option.split('-')
    #    sorted_articles = sorted(filtered_articles, key=attrgetter(field), reverse=order == 'desc')

    return render_template('catalog.html', articles=filtered_articles)


@catalog.route('/article/<int:id>')
def article_page(id):
    article = storage.get_article_by_id(id)
    return render_template('article.html', article=article)


@catalog.route('/clear-filters/<article_type>')
def clear_filters(article_type):
    session['price_start'] = ''
    session['price_end'] = ''
    return redirect(url_for('.catalog_page', article_type=article_type))
