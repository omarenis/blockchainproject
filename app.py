
from datetime import timedelta
import ipfsApi
import redis
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from os.path import dirname

ACCESS_EXPIRES = timedelta(hours=24)


class Config(object):
    DEBUG = True
    SECRET_KEY = 'helloworldrgpujefpeogzzfgùzegj$ezpgoj$zegpojze$gopjze$pgoje$zpgjez$gezokf$ezpokvgrz$pgojr$pgoj$emogkn'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{str(dirname(__file__))}/project.db'
    WTF_CSRF_SECRET_KEY = "esgmiezgijzegôpjzegpojzegozjegpojgeopgjezgoj"
    SESSION_TYPE = 'redis'
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = ACCESS_EXPIRES


class ConfigWithMailPort(Config):
    MAIL_SERVER = 'sandbox.smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME = '19a5b5ea2fc71d'
    MAIL_PASSWORD = 'd55b3b4a5703bf'
    MAIL_DEFAULT_SENDER = '19a5b5ea2fc71d'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    SESSION_TYPE = 'redis'


app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
client = ipfsApi.Client('127.0.0.1', 5001)
print(client)
mail = Mail(app=app)
db = SQLAlchemy(app=app)
jwt = JWTManager(app)
with app.app_context():
    db.create_all()
jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


DOMAIN = 'https://dev-lb7e3m3dx1tif6ur.us.auth0.com'
CLIENT_ID = 'q79iSXAN4soSeL1aAGg7UhxO1cK9zqAx'
CLIENT_SECRET = 'mlTYm9o-dRX01S01605C9F8-N_Jp1dzkJDPrV5bgh7DvYWWb7tmXS_CrUU7JhGyZ'
