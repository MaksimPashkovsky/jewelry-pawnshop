from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Message
from config import UrlSafeTimeSerializerConfig
from .. import mail


url_safe_timed_serializer = URLSafeTimedSerializer(UrlSafeTimeSerializerConfig.URL_SAFE_TIMED_SERIALIZER_SECRET_KEY)


def generate_token(email):
    return url_safe_timed_serializer.dumps(email, salt='salt')


def send_email(email, header, body):
    msg = Message(header, sender='jeweltry-shop@yahoo.com', recipients=[email])
    msg.body = body
    mail.send(msg)


def retrieve_email(token):
    try:
        email = url_safe_timed_serializer.loads(token, salt='salt', max_age=3600)
        return email
    except SignatureExpired:
        return False
