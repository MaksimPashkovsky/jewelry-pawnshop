from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import abort


__all__ = ['ProductView', 'Controller', 'CartNoteView', 'ProductTypeView', 'HistoryNoteView']


class ProductView(ModelView):
    column_list = ['name', 'type_object', 'price', 'quantity', 'image']


class Controller(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_admin:
            return True
        abort(404)

    def inaccessible_callback(self, name, **kwargs):
        return 'You have no permission'


class CartNoteView(ModelView):
    pass


class ProductTypeView(ModelView):
    pass


class HistoryNoteView(ModelView):
    pass
