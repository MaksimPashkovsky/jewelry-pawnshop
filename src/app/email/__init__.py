from flask import Blueprint

email = Blueprint('email', __name__, template_folder='templates', static_folder='static')

from . import views
