from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import abort, Markup, render_template_string
from app.models import *
from .db_setup import session
import base64


def add_all_views(admin):
    admin.add_view(Controller(User, session))
    admin.add_view(ArticleView(Article, session))
    admin.add_view(ArticleTypeView(ArticleType, session))
    admin.add_view(HistoryView(History, session))
    admin.add_view(AppraiserView(Appraiser, session))
    admin.add_view(AuctionView(Auction, session))
    admin.add_view(ConditionView(Condition, session))
    admin.add_view(CustomerView(Customer, session))
    admin.add_view(PassportInfoView(PassportInfo, session))
    admin.add_view(SoldLotView(SoldLot, session))
    admin.add_view(EstimationOrderView(EstimationOrder, session))


class EstimationOrderView(ModelView):
    can_edit = False
    can_create = False
    column_list = ['images', 'description', 'name', 'phone_number']

    def _list_thumbnail(self, context, model, name):
        if not model.images:
            return ''

        inner = ''

        template = """
            <div class="text-center">
                <a href="{}">
                    <img width="300" src="data:image/jpeg;base64,{}">
                </a>
            </div>
        """

        for i, image in enumerate(model.images):
            href = "{{ " + "url_for('main.getimage', order_id={}, file_num={})".format(model.order_id, i) + " }}"
            inner += template.format(href, str(base64.b64encode(image), "utf-8"))

        return Markup(render_template_string("{}".format(inner)))

    column_formatters = {
        'images': _list_thumbnail
    }


class ArticleView(ModelView):
    create_modal = True
    edit_modal = True
    can_export = True

    form_excluded_columns = ['users_have_in_cart', 'users_have_in_history', 'users_have_in_sold_lots']

    column_list = ['name', 'description', 'type', 'condition', 'weight', 'estimated_price', 'receipt_date',
                   'expiry_date', 'appraiser', 'customer', 'for_sale', 'image']

    column_filters = ('name', 'description', 'type', 'condition', 'weight', 'estimated_price', 'receipt_date',
                      'expiry_date', 'appraiser', 'customer', 'for_sale')

    def _list_thumbnail(self, context, model, name):
        if not model.image:
            return ""

        template = """
            <div class="text-center">
                <img width="300" src="/static/images/{}">
            </div>
        """

        return Markup(render_template_string(template.format(model.image)))

    def _show_description(self, context, model, name):
        if not model.description:
            return ""

        return model.description[:20] + "..."

    column_formatters = {
        'image': _list_thumbnail,
        'description': _show_description
    }


class Controller(ModelView):
    create_modal = True
    edit_modal = True
    can_create = False
    can_edit = False
    can_delete = False
    column_filters = ('login', 'email', 'registration_date', 'is_verified')

    def _show_password(self, context, model, name):
        if not model.password:
            return ""

        return model.password[:20] + "..."

    column_formatters = {
        'password': _show_password
    }

    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_admin:
            return True
        abort(403)
        return True

    def inaccessible_callback(self, name, **kwargs):
        return 'You have no permission'


class ArticleTypeView(ModelView):
    create_modal = True
    edit_modal = True
    column_filters = ['name']
    form_excluded_columns = ['articles']


class HistoryView(ModelView):
    create_modal = True
    edit_modal = True
    can_create = False
    can_edit = False
    can_delete = False
    column_filters = ['user', 'article', "date"]


class AppraiserView(ModelView):
    create_modal = True
    edit_modal = True
    can_create = False
    can_edit = False
    can_delete = False
    column_filters = ['user', 'salary', 'employment_date', 'name', 'surname', 'phone_number', 'date_of_birth', 'sex']


class AuctionView(ModelView):
    create_modal = True
    edit_modal = True
    column_list = ['name', 'date']
    column_filters = ['name', 'date']


class SoldLotView(ModelView):
    create_modal = True
    edit_modal = True
    column_filters = ['article', 'user', 'status', 'timestamp', 'start_sum', 'final_sum']

    def after_model_change(self, form, model, is_created):
        model.article.for_sale = False
        session.commit()


class ConditionView(ModelView):
    create_modal = True
    edit_modal = True
    column_filters = ['name']


class CustomerView(ModelView):
    create_modal = True
    edit_modal = True
    column_list = ['name', 'surname', 'phone_number', 'date_of_birth', 'sex', 'user', 'passport_object']
    column_filters = ['name', 'surname', 'phone_number', 'date_of_birth', 'sex', 'user', 'passport_object']


class PassportInfoView(ModelView):
    create_modal = True
    edit_modal = True
