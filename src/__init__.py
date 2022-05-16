from flask import Flask
from flask_login import LoginManager
from flask_toastr import Toastr
from flask_admin import Admin
from email_ import mail_service, email, Mail
import admin_views
from profile.profile import profile
from catalog.catalog import catalog
from cart.cart import cart
from config import AppConfig, MailConfig, ToastrConfig
from database_service import DatabaseService

app = Flask(__name__)

storage = DatabaseService()

app.secret_key = AppConfig.SECRET_KEY
app.config.from_object(MailConfig)
app.config.from_object(ToastrConfig)
app.jinja_env.globals['PRODUCT_TYPES'] = storage.get_all_product_types()

login_manager = LoginManager(app)
toastr = Toastr(app)
mail_service.mail = Mail(app)

admin_views.add_all_views(Admin(app))

app.register_blueprint(profile, url_prefix='/profile')
app.register_blueprint(email.email, url_prefix='/email')
app.register_blueprint(catalog, url_prefix='/catalog')
app.register_blueprint(cart, url_prefix='/cart')

from src import routes
