import sqlalchemy as sa
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from db_setup import Base


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    login = sa.Column('login', sa.String, unique=True)
    password = sa.Column('password', sa.String)
    email = sa.Column('email', sa.String)
    is_verified = sa.Column('is_verified', sa.Boolean)
    registration_date = sa.Column('registration date', sa.Date)

    def __init__(self, login, password, email, reg_date, is_verified):
        self.login = login
        self.password = password
        self.email = email
        self.registration_date = reg_date
        self.is_verified = is_verified


class Product(Base):
    __tablename__ = 'products'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column('name', sa.String)
    type = sa.Column('type', sa.Integer, sa.ForeignKey("product_types.id"))
    price = sa.Column('price', sa.Numeric)
    quantity = sa.Column('quantity', sa.Integer)
    image = sa.Column('image', sa.String)
    type_object = relationship('ProductType')


class ProductType(Base):
    __tablename__ = 'product_types'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column('name', sa.String)


class CartNote(Base):
    __tablename__ = 'carts'

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    product_id = sa.Column(sa.Integer, sa.ForeignKey("products.id"))
    user = relationship("User")
    product = relationship("Product")

    def __init__(self, user_id, product_id):
        self.user_id = user_id
        self.product_id = product_id