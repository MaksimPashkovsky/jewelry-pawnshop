from app.models import *
from app.db_setup import session


class DatabaseService:

    def __init__(self):
        self.session = session

    def get_all_article_types(self):
        return self.session.query(ArticleType).all()

    def get_all_articles_for_sale(self):
        return self.session.query(Article).filter_by(for_sale=True).all()

    def get_article_by_id(self, ar_id):
        return self.session.query(Article).filter_by(article_id=ar_id).first()

    def get_article_type_by_name(self, name):
        return self.session.query(ArticleType).filter_by(name=name).first()

    def get_all_logins(self):
        return [item[0] for item in self.session.query(User.login).all()]

    def get_all_emails(self):
        return [item[0] for item in self.session.query(User.email).all()]

    def save(self, new_obj):
        self.session.add(new_obj)
        self.session.commit()

    def delete(self, obj_to_delete):
        self.session.delete(obj_to_delete)
        self.session.commit()

    def get_user_by_email(self, email):
        return self.session.query(User).filter_by(email=email).first()

    def get_user_by_login(self, login):
        return self.session.query(User).filter_by(login=login).first()

    def get_user_by_id(self, user_id):
        return self.session.query(User).get(user_id)

    def is_user_admin(self, user):
        if user.user_id in [a.user_id for a in self.session.query(Appraiser).all()]:
            return True
        return False

    def get_estimation_order_by_id(self, o_id):
        return self.session.query(EstimationOrder).filter_by(order_id=o_id).first()
