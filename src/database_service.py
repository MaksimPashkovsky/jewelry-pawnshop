from db_setup import session
from models import ProductType, User, Product, CartNote


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

    def get_all_product_types(self):
        return self.session.query(ProductType).all()

    def get_product_type_by_name(self, name):
        return self.session.query(ProductType).filter_by(name=name).first()

    def get_products_by_type(self, type: int):
        return self.session.query(Product).filter_by(type=type).all()

    def get_product_by_id(self, pr_id):
        return self.session.query(Product).filter_by(id=pr_id).first()

    def get_user_by_id(self, user_id):
        return self.session.query(User).get(user_id)

    def get_user_by_login(self, login):
        return self.session.query(User).filter_by(login=login).first()

    def get_user_by_email(self, email):
        return self.session.query(User).filter_by(email=email).first()

    def get_all_products(self):
        return self.session.query(Product).all()

    def get_cart_note(self, user_id, product_id):
        return self.session.query(CartNote).filter_by(user_id=user_id, product_id=product_id).first()

    def get_cart_notes_by_user_id(self, user_id):
        return self.session.query(CartNote).filter_by(user_id=user_id).all()

    def save(self, new_obj):
        self.session.add(new_obj)
        self.session.commit()

    def delete(self, obj_to_delete):
        self.session.delete(obj_to_delete)
        self.session.commit()

    def delete_cart_notes_by_user_id(self, user_id):
        self.session.query(CartNote).filter_by(user_id=user_id).delete(synchronize_session='fetch')
        self.session.commit()

    def get_all_logins(self):
        return [item[0] for item in self.session.query(User.login).all()]

    def get_all_emails(self):
        return [item[0] for item in self.session.query(User.email).all()]

    def get_user_column(self, field: str):
        return [item[0] for item in self.session.query(getattr(User, field)).all()]