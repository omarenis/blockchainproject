from flask import Flask
from flask_mail import Mail, Message
from flask_login import UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy
from os.path import dirname
from flask_session import Session


class Config(object):
    DEBUG = True
    SECRET_KEY = 'helloworldrgpujefpeogzemogkn'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{str(dirname(__file__))}/project.db'
    SESSION_TYPE = 'redis'


class ConfigWithMailPort(Config):
    MAIL_SERVER = 'sandbox.smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME = '19a5b5ea2fc71d'
    MAIL_PASSWORD = 'd55b3b4a5703bf'
    MAIL_DEFAULT_SENDER = '19a5b5ea2fc71d'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False


app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app=app)
login_manager = LoginManager(app=app)
login_manager.login_view = '/login'
db = SQLAlchemy(app=app)
session = Session(app=app)
with app.app_context():
    db.create_all()
DOMAIN = 'https://dev-lb7e3m3dx1tif6ur.us.auth0.com'
CLIENT_ID = 'q79iSXAN4soSeL1aAGg7UhxO1cK9zqAx'
CLIENT_SECRET = 'mlTYm9o-dRX01S01605C9F8-N_Jp1dzkJDPrV5bgh7DvYWWb7tmXS_CrUU7JhGyZ'
