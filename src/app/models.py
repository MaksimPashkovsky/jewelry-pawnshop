from typing import List
from flask_login import UserMixin
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db_setup import Base
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Date, ForeignKey, Table, TIMESTAMP, Float, ARRAY, \
    LargeBinary

__all__ = ['Appraiser', 'Article', 'ArticleType', 'Auction', 'Condition', 'Customer', 'PassportInfo', 'User', 'History',
           'SoldLot', 'EstimationOrder']


class Person:
    person_id = Column(Integer, primary_key=True)

    name = Column(String)
    surname = Column(String)
    phone_number = Column(String)
    date_of_birth = Column(Date)
    sex = Column(Boolean)

    def __init__(self, name=None, surname=None, phone_number=None, date_of_birth=None, sex=None):
        self.name = name
        self.surname = surname
        self.phone_number = phone_number
        self.date_of_birth = date_of_birth
        self.sex = sex


class Appraiser(Person, Base):
    __tablename__ = 'Appraiser'

    user_id = Column(Integer, ForeignKey("User.user_id"))

    salary = Column(Float)
    employment_date = Column(Date)

    user: Mapped['User'] = relationship(back_populates='appraiser')

    def __repr__(self):
        return " ".join((self.surname, self.name))


cart = Table('cart',
             Base.metadata,
             Column('user_id', Integer, ForeignKey('User.user_id'), primary_key=True),
             Column('article_id', Integer, ForeignKey('Article.article_id'), primary_key=True))


class History(Base):
    __tablename__ = 'history'

    user_id: Mapped[int] = mapped_column(ForeignKey('User.user_id'), primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey('Article.article_id'), primary_key=True)

    date = Column(Date)

    user: Mapped['User'] = relationship(back_populates='articles_in_history')
    article: Mapped['Article'] = relationship(back_populates='users_have_in_history')


class Article(Base):
    __tablename__ = 'Article'

    article_id = Column(Integer, primary_key=True)

    condition_id = Column(Integer, ForeignKey('Condition.condition_id'))
    appraiser_id = Column(Integer, ForeignKey('Appraiser.person_id'))
    customer_id = Column(Integer, ForeignKey('Customer.person_id'))
    type_id = Column(Integer, ForeignKey("ArticleType.type_id"))

    name = Column(String)
    weight = Column(Numeric)
    estimated_price = Column(Numeric)
    receipt_date = Column(Date)
    expiry_date = Column(Date)
    image = Column(String)
    for_sale = Column(Boolean)

    type: Mapped['ArticleType'] = relationship(back_populates='articles')
    condition = relationship("Condition")
    appraiser = relationship("Appraiser")
    customer = relationship("Customer")

    users_have_in_cart: Mapped[List['User']] = relationship(secondary=cart, back_populates='articles_in_cart')
    users_have_in_history: Mapped[List['History']] = relationship(back_populates='article')
    users_have_in_sold_lots: Mapped[List['SoldLot']] = relationship(back_populates='article')

    def __repr__(self):
        return "{}, ${}".format(self.name, self.estimated_price)


class ArticleType(Base):
    __tablename__ = 'ArticleType'

    type_id = Column(Integer, primary_key=True)

    name = Column(String)

    articles: Mapped[List['Article']] = relationship(back_populates='type')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Auction(Base):
    __tablename__ = 'Auction'

    auction_id = Column(Integer, primary_key=True)

    date = Column(Date)
    name = Column(String)


class Condition(Base):
    __tablename__ = 'Condition'

    condition_id = Column(Integer, primary_key=True)

    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Customer(Person, Base):
    __tablename__ = 'Customer'

    passport_id = Column(Integer, ForeignKey('PassportInfo.passport_id'))
    user_id = Column(Integer, ForeignKey("User.user_id"))

    discount = Column(Numeric)

    passport_object = relationship('PassportInfo')
    user: Mapped['User'] = relationship(back_populates='customer')

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

    passport_id = Column(Integer, primary_key=True)

    type = Column(String)
    code_of_issuing_state = Column(String)
    passport_number = Column(String)
    surname = Column(String)
    name = Column(String)
    nationality = Column(String)
    date_of_birth = Column(Date)
    identification_number = Column(String)
    sex = Column(Boolean)
    place_of_birth = Column(String)
    date_of_issue = Column(Date)
    date_of_expiry = Column(Date)
    authority = Column(String)

    def __repr__(self):
        return " ".join((self.surname, self.name, self.identification_number))


class User(UserMixin, Base):
    __tablename__ = 'User'

    user_id = Column(Integer, primary_key=True)

    login = Column(String, unique=True)
    password = Column(String)
    email = Column(String, unique=True)
    registration_date = Column(Date)
    is_verified = Column(Boolean)

    appraiser: Mapped['Appraiser'] = relationship(back_populates='user')
    customer: Mapped['Customer'] = relationship(back_populates='user')
    articles_in_cart: Mapped[List[Article]] = relationship(secondary=cart, back_populates='users_have_in_cart')
    articles_in_history: Mapped[List['History']] = relationship(back_populates='user')
    articles_in_sold_lots: Mapped[List['SoldLot']] = relationship(back_populates='user')

    def get_id(self):
        return self.user_id

    @property
    def is_admin(self):
        return self.appraiser is not None

    def __init__(self, login, password, email, reg_date, is_verified=False):
        self.login = login
        self.password = password
        self.email = email
        self.registration_date = reg_date
        self.is_verified = is_verified

    def __repr__(self):
        return self.login


class SoldLot(Base):
    __tablename__ = 'SoldLot'

    lot_id = Column(Integer, primary_key=True)
    auction_id = Column(Integer, ForeignKey('Auction.auction_id'))
    article_id = Column(Integer, ForeignKey('Article.article_id'))
    user_id = Column(Integer, ForeignKey('User.user_id'))

    status = Column(String)
    timestamp = Column(TIMESTAMP)
    start_sum = Column(Float)
    final_sum = Column(Float)

    article: Mapped[Article] = relationship(back_populates='users_have_in_sold_lots')
    user: Mapped[User] = relationship(back_populates='articles_in_sold_lots')


class EstimationOrder(Base):
    __tablename__ = 'EstimationOrder'

    order_id = Column(Integer, primary_key=True)
    name = Column(String)
    phone_number = Column(String)
    description = Column(String)
    images = Column(ARRAY(LargeBinary))

    def __init__(self, name, phone_number, desc, imgs):
        self.name = name
        self.phone_number = phone_number
        self.description = desc
        self.images = imgs
