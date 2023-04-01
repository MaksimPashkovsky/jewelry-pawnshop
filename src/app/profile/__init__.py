from flask import Blueprint

profile = Blueprint('profile', __name__, template_folder='templates', static_folder='static')

from . import views
