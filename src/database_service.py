from db_setup import session
from models import *


class DatabaseService:
    _instance = None
    session = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.__init__(cls._instance)
        return cls._instance

    def __init__(self):
        self.session = session

    def get_all_article_types(self):
        return self.session.query(ArticleType).all()

    def get_all_articles(self):
        return self.session.query(Article).all()

    def get_article_by_id(self, ar_id):
        return self.session.query(Article).filter_by(article_id=ar_id).first()

    def get_all_history_notes_by_article_id(self, article_id):
        return self.session.query(HistoryNote).filter_by(article_id=article_id).all()

    def get_article_type_by_name(self, name):
        return self.session.query(ArticleType).filter_by(name=name).first()

    def get_articles_by_type_id(self, type_id: int):
        return self.session.query(Article).filter_by(type_id=type_id).all()

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

    def get_cart_notes_by_user_id(self, user_id):
        return self.session.query(CartNote).filter_by(user_id=user_id).all()

    def get_cart_note(self, user_id, article_id):
        return self.session.query(CartNote).filter_by(user_id=user_id, article_id=article_id).first()

    def delete_cart_notes_by_user_id(self, user_id):
        self.session.query(CartNote).filter_by(user_id=user_id).delete(synchronize_session='fetch')
        self.session.commit()

    def get_user_column(self, field: str):
        return [item[0] for item in self.session.query(getattr(User, field)).all()]

    def get_all_history_notes_by_user_id(self, user_id):
        return self.session.query(HistoryNote).filter_by(user_id=user_id).all()

