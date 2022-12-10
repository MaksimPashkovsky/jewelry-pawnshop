from operator import attrgetter
from difflib import SequenceMatcher
from flask import Blueprint, request, render_template, session, redirect, url_for
from database_service import DatabaseService

catalog = Blueprint('catalog', __name__, template_folder='templates', static_folder='static')
storage = DatabaseService()


@catalog.route('/<article_type>', methods=['GET', 'POST'])
def catalog_page(article_type):

    article_type_object = storage.get_article_type_by_name(article_type.capitalize())

    # All articles of concrete type
    all_articles = storage.get_articles_by_type_id(article_type_object.type_id)

    if request.method == 'GET':
        return render_template('catalog/catalog.html', article_type=article_type,
                               articles=sorted(all_articles, key=attrgetter('name')))

    search_string = request.form.get('search-string')

    if search_string:
        all_articles = list(filter(lambda x: SequenceMatcher(None, search_string, x.name).ratio() >= 0.3, all_articles))

    price_start = request.form.get('price-start')
    price_end = request.form.get('price-end')

    if price_start == '' and all_articles:
        price_start = min(all_articles, key=attrgetter('price')).price

    if price_end == '' and all_articles:
        price_end = max(all_articles, key=attrgetter('price')).price

    filtered_articles = list(filter(lambda x: float(price_start) <= x.price <= float(price_end), all_articles))

    session['price_start'] = price_start
    session['price_end'] = price_end

    sorting_option = request.form.get('sorting')

    if sorting_option == 'num-of-purchased':
        sorted_articles = sorted(filtered_articles, key=lambda x: len(storage.get_all_history_notes_by_article_id(x.article_id)), reverse=True)
    else:
        field, order = sorting_option.split('-')
        sorted_articles = sorted(filtered_articles, key=attrgetter(field), reverse=order == 'desc')

    return render_template('catalog/catalog.html', article_type=article_type, articles=sorted_articles,
                           sorting_option=sorting_option)


@catalog.route('/article/<id>')
def article_page(id):
    article = storage.get_article_by_id(id)
    num_of_purchases = len(storage.get_all_history_notes_by_article_id(id))
    return render_template('catalog/article.html', article=article, num_of_purchases=num_of_purchases)


@catalog.route('/clear-filters/<article_type>')
def clear_filters(article_type):
    session['price_start'] = ''
    session['price_end'] = ''
    return redirect(url_for('.catalog_page', article_type=article_type))