from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import abort, Markup, render_template_string
from app.models import *
from .db_setup import session


def add_all_views(admin):
    admin.add_view(Controller(User, session))
    admin.add_view(ArticleView(Article, session))
    admin.add_view(ModelView(ArticleType, session))
    admin.add_view(ModelView(History, session))
    admin.add_view(ModelView(Appraiser, session))
    admin.add_view(ModelView(Auction, session))
    admin.add_view(ModelView(Condition, session))
    admin.add_view(ModelView(Customer, session))
    admin.add_view(ModelView(PassportInfo, session))
    admin.add_view(ModelView(SoldLot, session))
    admin.add_view(EstimationOrderView(EstimationOrder, session))


class EstimationOrderView(ModelView):

    def _list_thumbnail(self, context, model, name):
        if not model.images:
            return ''

        inner = ''

        template = """
            <li>
                <a href="{}">
                    image{}
                </a>
            </li>
        """

        for i in range(len(model.images)):
            href = "{{ " + "url_for('main.getimage', order_id={}, file_num={})".format(model.order_id, i) + " }}"

            inner += template.format(href, i)

        return Markup(render_template_string("<ul>{}</ul>".format(inner)))

    column_formatters = {
        'images': _list_thumbnail
    }


class ArticleView(ModelView):
    column_list = ['name', 'type', 'condition', 'weight',
                   'estimated_price', 'receipt_date', 'expiry_date', 'appraiser', 'customer', 'for_sale', 'image']


class Controller(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_admin:
            return True
        abort(403)
        return True

    def inaccessible_callback(self, name, **kwargs):
        return 'You have no permission'
