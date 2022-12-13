import sqlalchemy as sa
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from db_setup import Base

__all__ = ['Account', 'Appraiser', 'Article', 'ArticleType',
           'Auction', 'Condition', 'Customer', 'PassportInfo',
           'SoldLot', 'User', 'CartNote', 'HistoryNote']


class Account(Base):
    __tablename__ = 'Account'

    account_id = sa.Column(sa.Integer, primary_key=True)
    bank = sa.Column(sa.String)
    account_number = sa.Column(sa.String)
    balance = sa.Column(sa.Numeric)

    def __init__(self, bank, account_number, balance=0):
        self.bank = bank
        self.account_number = account_number
        self.balance = balance

    def __repr__(self):
        return self.account_number


class Person:
    person_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    surname = sa.Column(sa.String)
    phone_number = sa.Column(sa.String)
    date_of_birth = sa.Column(sa.Date)
    sex = sa.Column(sa.Boolean)

    def __init__(self, name=None, surname=None, phone_number=None, date_of_birth=None, sex=None):
        self.name = name
        self.surname = surname
        self.phone_number = phone_number
        self.date_of_birth = date_of_birth
        self.sex = sex


class Appraiser(Person, Base):
    __tablename__ = 'Appraiser'

    # position = sa.Column(sa.String)
    salary = sa.Column(sa.Numeric)
    employment_date = sa.Column(sa.Date)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("User.user_id"))

    def __repr__(self):
        return " ".join((self.surname, self.name))


class Article(Base):
    __tablename__ = 'Article'

    article_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    condition_id = sa.Column(sa.Integer, sa.ForeignKey('Condition.condition_id'))
    condition = relationship("Condition")
    weight = sa.Column(sa.Numeric)
    estimated_price = sa.Column(sa.Numeric)
    receipt_date = sa.Column(sa.Date)
    expiry_date = sa.Column(sa.Date)
    appraiser_id = sa.Column(sa.Integer, sa.ForeignKey('Appraiser.person_id'))
    appraiser = relationship("Appraiser")
    customer_id = sa.Column(sa.Integer, sa.ForeignKey('Customer.person_id'))
    customer = relationship("Customer")
    type_id = sa.Column(sa.Integer, sa.ForeignKey("ArticleType.type_id"))
    type = relationship("ArticleType")
    quantity = sa.Column(sa.Integer)
    image = sa.Column(sa.String)
    for_sale = sa.Column(sa.Boolean)

    def __repr__(self):
        return "{}, ${}".format(self.name, self.estimated_price)


class ArticleType(Base):
    __tablename__ = 'ArticleType'

    type_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    def __repr__(self):
        return self.name


class Auction(Base):
    __tablename__ = 'Auction'

    auction_id = sa.Column(sa.Integer, primary_key=True)
    date = sa.Column(sa.Date)
    name = sa.Column(sa.String)


class Condition(Base):
    __tablename__ = 'Condition'

    condition_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    def __repr__(self):
        return self.name


class Customer(Person, Base):
    __tablename__ = 'Customer'

    discount = sa.Column(sa.Numeric)
    passport_id = sa.Column(sa.Integer, sa.ForeignKey('PassportInfo.passport_id'))
    passport_object = relationship('PassportInfo')
    user_id = sa.Column(sa.Integer, sa.ForeignKey("User.user_id"))
    user = relationship("User")

    def __init__(self, user_id, discount=0):
        Person.__init__(self)
        self.user_id = user_id
        self.discount = discount

    def __repr__(self):
        try:
            string = " ".join((self.surname, self.name))
        except Exception:
            string = self.user.login
        return string


class PassportInfo(Base):
    __tablename__ = 'PassportInfo'

    passport_id = sa.Column(sa.Integer, primary_key=True)
    type = sa.Column(sa.String)
    code_of_issuing_state = sa.Column(sa.String)
    passport_number = sa.Column(sa.String)
    surname = sa.Column(sa.String)
    name = sa.Column(sa.String)
    nationality = sa.Column(sa.String)
    date_of_birth = sa.Column(sa.Date)
    identification_number = sa.Column(sa.String)
    sex = sa.Column(sa.Boolean)
    place_of_birth = sa.Column(sa.String)
    date_of_issue = sa.Column(sa.Date)
    date_of_expiry = sa.Column(sa.Date)
    authority = sa.Column(sa.String)

    def __repr__(self):
        return " ".join((self.surname, self.name, self.identification_number))


class SoldLot(Base):
    __tablename__ = 'SoldLot'

    lot_id = sa.Column(sa.Integer, primary_key=True)
    article_id = sa.Column(sa.Integer, sa.ForeignKey("Article.article_id"))
    auction_id = sa.Column(sa.Integer, sa.ForeignKey("Auction.auction_id"))
    user_id = sa.Column(sa.Integer, sa.ForeignKey("User.user_id"))
    status = sa.Column(sa.String)
    timestamp = sa.Column(sa.TIMESTAMP)
    start_sum = sa.Column(sa.Float)
    final_sum = sa.Column(sa.Float)


class User(Base, UserMixin):
    __tablename__ = 'User'

    user_id = sa.Column(sa.Integer, primary_key=True)
    login = sa.Column(sa.String, unique=True)
    password = sa.Column(sa.String)
    email = sa.Column(sa.String, unique=True)
    registration_date = sa.Column(sa.Date)
    is_verified = sa.Column(sa.Boolean)
    account_id = sa.Column(sa.Integer, sa.ForeignKey("Account.account_id"))
    account = relationship("Account", foreign_keys=[account_id])

    def __init__(self, login, password, email, reg_date, account_id, is_verified=False):
        self.login = login
        self.password = password
        self.email = email
        self.registration_date = reg_date
        self.account_id = account_id
        self.is_verified = is_verified

    def get_id(self):
        return self.user_id

    def __repr__(self):
        return self.login


class CartNote(Base):
    __tablename__ = 'Cart'

    cart_id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("User.user_id"))
    article_id = sa.Column(sa.Integer, sa.ForeignKey("Article.article_id"))
    article = relationship("Article")

    def __init__(self, user_id, article_id):
        self.user_id = user_id
        self.article_id = article_id


class HistoryNote(Base):
    __tablename__ = 'History'

    history_id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("User.user_id"))
    article_id = sa.Column(sa.Integer, sa.ForeignKey("Article.article_id"))
    article = relationship("Article")
    date = sa.Column(sa.Date)

    def __init__(self, user_id, article_id, date):
        self.user_id = user_id
        self.article_id = article_id
        self.date = date
