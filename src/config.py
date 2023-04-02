from decouple import config


class Config:
    pass


class DatabaseConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost:5432/pawnshop-db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class AppConfig(Config):
    SECRET_KEY = config('APP_SECRET_KEY')


class UrlSafeTimeSerializerConfig(Config):
    URL_SAFE_TIMED_SERIALIZER_SECRET_KEY = config('URL_SAFE_TIMED_SERIALIZER_SECRET_KEY')


class MailConfig(Config):
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'pashkovskij_ma_19@mf.grsu.by'
    MAIL_PASSWORD = config('MAIL_PASSWORD')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True


class ToastrConfig(Config):
    TOASTR_POSITION_CLASS = 'toast-bottom-right'
    TOASTR_PROGRESS_BAR = 'false'
    TOASTR_TIMEOUT = 5000
