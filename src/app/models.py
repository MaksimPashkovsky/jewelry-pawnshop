from flask_login import UserMixin
from . import db

__all__ = ['Account', 'Appraiser', 'Article', 'ArticleType',
           'Auction', 'Condition', 'Customer', 'PassportInfo', 'User', 'History']


class Account(db.Model):
    __tablename__ = 'Account'

    account_id = db.Column(db.Integer, primary_key=True)
    bank = db.Column(db.String)
    account_number = db.Column(db.String)
    balance = db.Column(db.Numeric)

    def __init__(self, bank, account_number, balance=0):
        self.bank = bank
        self.account_number = account_number
        self.balance = balance

    def __repr__(self):
        return self.account_number


class Person:
    person_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    surname = db.Column(db.String)
    phone_number = db.Column(db.String)
    date_of_birth = db.Column(db.Date)
    sex = db.Column(db.Boolean)

    def __init__(self, name=None, surname=None, phone_number=None, date_of_birth=None, sex=None):
        self.name = name
        self.surname = surname
        self.phone_number = phone_number
        self.date_of_birth = date_of_birth
        self.sex = sex


class Appraiser(Person, db.Model):
    __tablename__ = 'Appraiser'

    # position = db.Column(db.String)
    salary = db.Column(db.Numeric)
    employment_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey("User.user_id"))

    def __repr__(self):
        return " ".join((self.surname, self.name))


cart = db.Table('cart',
                db.Column('user_id', db.Integer, db.ForeignKey('User.user_id'), primary_key=True),
                db.Column('article_id', db.Integer, db.ForeignKey('Article.article_id'), primary_key=True))


class History(db.Model):
    __tablename__ = 'history'
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('Article.article_id'), primary_key=True)
    date = db.Column(db.Date)

    user = db.relationship('User',
                           backref=db.backref('history_notes', lazy='dynamic'))

    article = db.relationship('Article',
                              backref=db.backref('history_notes', lazy='dynamic'))


class Article(db.Model):
    __tablename__ = 'Article'

    article_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    condition_id = db.Column(db.Integer, db.ForeignKey('Condition.condition_id'))
    condition = db.relationship("Condition")
    weight = db.Column(db.Numeric)
    estimated_price = db.Column(db.Numeric)
    receipt_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    appraiser_id = db.Column(db.Integer, db.ForeignKey('Appraiser.person_id'))
    appraiser = db.relationship("Appraiser")
    customer_id = db.Column(db.Integer, db.ForeignKey('Customer.person_id'))
    customer = db.relationship("Customer")
    type_id = db.Column(db.Integer, db.ForeignKey("ArticleType.type_id"))
    type = db.relationship("ArticleType")
    quantity = db.Column(db.Integer)
    image = db.Column(db.String)
    for_sale = db.Column(db.Boolean)

    def __repr__(self):
        return "{}, ${}".format(self.name, self.estimated_price)


class ArticleType(db.Model):
    __tablename__ = 'ArticleType'

    type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return self.name


class Auction(db.Model):
    __tablename__ = 'Auction'

    auction_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    name = db.Column(db.String)


class Condition(db.Model):
    __tablename__ = 'Condition'

    condition_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Customer(Person, db.Model):
    __tablename__ = 'Customer'

    discount = db.Column(db.Numeric)
    passport_id = db.Column(db.Integer, db.ForeignKey('PassportInfo.passport_id'))
    passport_object = db.relationship('PassportInfo')
    user_id = db.Column(db.Integer, db.ForeignKey("User.user_id"))
    user = db.relationship("User")

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


class PassportInfo(db.Model):
    __tablename__ = 'PassportInfo'

    passport_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    code_of_issuing_state = db.Column(db.String)
    passport_number = db.Column(db.String)
    surname = db.Column(db.String)
    name = db.Column(db.String)
    nationality = db.Column(db.String)
    date_of_birth = db.Column(db.Date)
    identification_number = db.Column(db.String)
    sex = db.Column(db.Boolean)
    place_of_birth = db.Column(db.String)
    date_of_issue = db.Column(db.Date)
    date_of_expiry = db.Column(db.Date)
    authority = db.Column(db.String)

    def __repr__(self):
        return " ".join((self.surname, self.name, self.identification_number))


class User(db.Model, UserMixin):
    __tablename__ = 'User'

    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    registration_date = db.Column(db.Date)
    is_verified = db.Column(db.Boolean)
    account_id = db.Column(db.Integer, db.ForeignKey("Account.account_id"))
    account = db.relationship("Account", foreign_keys=[account_id])

    articles_in_cart = db.relationship('Article',
                                       secondary=cart,
                                       backref=db.backref('users_have_in_cart', lazy='dynamic'),
                                       lazy='dynamic')

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


sold_lot = db.Table('sold_lot',
                    db.Column('article_id', db.Integer, db.ForeignKey(Article.article_id), primary_key=True),
                    db.Column('auction_id', db.Integer, db.ForeignKey(Auction.auction_id), primary_key=True),
                    db.Column('user_id', db.Integer, db.ForeignKey(User.user_id)),
                    db.Column('status', db.String),
                    db.Column('timestamp', db.TIMESTAMP),
                    db.Column('start_sum', db.Float),
                    db.Column('final_sum', db.Float))
