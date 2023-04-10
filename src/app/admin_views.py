from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import abort
from app.models import *
from .db_setup import session


def add_all_views(admin):
    admin.add_view(Controller(User, session))
    admin.add_view(ArticleView(Article, session))
    admin.add_view(ModelView(ArticleType, session))
    admin.add_view(ModelView(History, session))
    admin.add_view(ModelView(Account, session))
    admin.add_view(ModelView(Appraiser, session))
    admin.add_view(ModelView(Auction, session))
    admin.add_view(ModelView(Condition, session))
    admin.add_view(ModelView(Customer, session))
    admin.add_view(ModelView(PassportInfo, session))
    admin.add_view(ModelView(SoldLot, session))


class ArticleView(ModelView):
    column_list = ['name', 'type', 'condition', 'weight', 'quantity',
                   'estimated_price', 'receipt_date', 'expiry_date', 'appraiser', 'customer', 'for_sale', 'image']


class Controller(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_admin:
            return True
        abort(403)
        return True

    def inaccessible_callback(self, name, **kwargs):
        return 'You have no permission'
