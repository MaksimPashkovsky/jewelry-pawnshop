from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import abort
from app.models import *
from app import storage


def add_all_views(admin):
    admin.add_view(Controller(User, storage.session))
    admin.add_view(ArticleView(Article, storage.session))
    admin.add_view(CartNoteView(CartNote, storage.session))
    admin.add_view(ArticleTypeView(ArticleType, storage.session))
    admin.add_view(HistoryNoteView(HistoryNote, storage.session))
    admin.add_view(AccountView(Account, storage.session))
    admin.add_view(AppraiserView(Appraiser, storage.session))
    admin.add_view(AuctionView(Auction, storage.session))
    admin.add_view(ConditionView(Condition, storage.session))
    admin.add_view(CustomerView(Customer, storage.session))
    admin.add_view(PassportInfoView(PassportInfo, storage.session))
    admin.add_view(SoldLotView(SoldLot, storage.session))


class ArticleView(ModelView):
    column_list = ['name', 'type', 'condition', 'weight', 'quantity',
                   'estimated_price', 'receipt_date', 'expiry_date','appraiser', 'customer', 'for_sale', 'image']


class Controller(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and storage.is_user_admin(current_user):
            return True
        abort(404)
        return True

    def inaccessible_callback(self, name, **kwargs):
        return 'You have no permission'


class CartNoteView(ModelView):
    pass


class ArticleTypeView(ModelView):
    pass


class HistoryNoteView(ModelView):
    pass


class AccountView(ModelView):
    pass


class AppraiserView(ModelView):
    pass


class AuctionView(ModelView):
    pass


class ConditionView(ModelView):
    pass


class CustomerView(ModelView):
    pass


class PassportInfoView(ModelView):
    pass


class SoldLotView(ModelView):
    pass
