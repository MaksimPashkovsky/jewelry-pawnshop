from flask import Flask
from flask_login import LoginManager
from flask_toastr import Toastr
from flask_admin import Admin
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from config import DatabaseConfig, AppConfig, UrlSafeTimeSerializerConfig, MailConfig, ToastrConfig

db = SQLAlchemy()
from database_service import DatabaseService
storage = DatabaseService(db)
login_manager = LoginManager()
admin = Admin()
toastr = Toastr()
mail = Mail()


@login_manager.user_loader
def load_user(user_id):
    return storage.get_user_by_id(user_id)


def create_app():
    app = Flask(__name__)

    app.config.from_object(DatabaseConfig)
    app.config.from_object(AppConfig)
    app.config.from_object(UrlSafeTimeSerializerConfig)
    app.config.from_object(MailConfig)
    app.config.from_object(ToastrConfig)

    db.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)
    toastr.init_app(app)
    mail.init_app(app)

    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
