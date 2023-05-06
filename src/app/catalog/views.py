from operator import attrgetter
from flask import request, render_template, session, redirect, url_for
from . import catalog
from app import storage


@catalog.route('/', methods=['GET', 'POST'])
def catalog_page():

    for a_type in ['ring', 'bracelet', 'watch', 'necklace', 'pendant', 'chain', 'earrings', 'brooch']:
        session['match-' + a_type] = ''

    if request.method == 'GET':
        all_articles = storage.get_all_articles_for_sale()
        return render_template('catalog.html', articles=sorted(all_articles, key=attrgetter('name')))

    articles = list()

    for a_type in ['ring', 'bracelet', 'watch', 'necklace', 'pendant', 'chain', 'earrings', 'brooch']:
        if request.form.get('match-' + a_type):
            articles.extend(storage.get_article_type_by_name(a_type.capitalize()).articles)
            session['match-' + a_type] = 'checked'

    price_start = request.form.get('price-start')
    price_end = request.form.get('price-end')

    filtered_articles = list(filter(lambda x: float(price_start) <= x.estimated_price <= float(price_end), articles))

    #sorting_option = request.form.get('sorting')

    #if sorting_option == 'num-of-purchased':
    #    sorted_articles = sorted(filtered_articles, key=lambda x: len(x.users_have_in_history), reverse=True)
    #else:
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