from flask import Blueprint

cart = Blueprint('cart', __name__, template_folder='templates', static_folder='static')

from . import views
