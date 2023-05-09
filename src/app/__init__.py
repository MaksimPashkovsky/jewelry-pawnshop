from flask import Flask
from flask_login import LoginManager
from flask_toastr import Toastr
from flask_admin import Admin
from flask_mail import Mail
from config import AppConfig, UrlSafeTimeSerializerConfig, MailConfig, ToastrConfig
from app.database_service import DatabaseService
from .models import *
from .db_setup import Base, engine
from app.admin_views import add_all_views

storage = DatabaseService()
login_manager = LoginManager()
admin = Admin()
toastr = Toastr()
mail = Mail()


@login_manager.user_loader
def load_user(user_id):
    return storage.get_user_by_id(user_id)


def create_app():
    app = Flask(__name__)

    app.config.from_object(AppConfig)
    app.config.from_object(UrlSafeTimeSerializerConfig)
    app.config.from_object(MailConfig)
    app.config.from_object(ToastrConfig)

    login_manager.init_app(app)
    admin.init_app(app)
    toastr.init_app(app)
    mail.init_app(app)

    @app.shell_context_processor
    def make_shell_context():
        return dict(Base=Base, engine=engine, User=User, Article=Article, History=History)

    @app.context_processor
    def inject_types():
        return dict(TYPES=storage.get_all_article_types())

    from .main import main as main_blueprint
    from .cart import cart as cart_blueprint
    from .catalog import catalog as catalog_blueprint
    from .email import email as email_blueprint
    from .profile import profile as profile_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(cart_blueprint, url_prefix='/cart')
    app.register_blueprint(catalog_blueprint, url_prefix='/catalog')
    app.register_blueprint(email_blueprint, url_prefix='/email')
    app.register_blueprint(profile_blueprint, url_prefix='/profile')

    add_all_views(admin)

    return app
