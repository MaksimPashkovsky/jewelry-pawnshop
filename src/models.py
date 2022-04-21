import sqlalchemy as sa
from db_setup import Base
from flask_login import UserMixin


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    login = sa.Column('login', sa.String, unique=True)
    password = sa.Column('password', sa.String)
    registration_date = sa.Column('registration date', sa.Date)

    def __init__(self, login, password, reg_date):
        self.login = login
        self.password = password
        self.registration_date = reg_date


class Product(Base):
    __tablename__ = 'products'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column('name', sa.String)
    type = sa.Column('type', sa.String)
    price = sa.Column('price', sa.Numeric)
    quantity = sa.Column('quantity', sa.Integer)


class ProductType(Base):
    __tablename__ = 'product_types'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column('name', sa.String)

    def __repr__(self):
        return f'ProductType(id={self.id}, name={self.name})'
