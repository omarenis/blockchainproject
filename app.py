from flask import Flask
from flask_mail import Mail, Message
from flask_login import UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    SECRET_KEY = 'helloworldrgpujefpeogzemogkn'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///project.db'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = "omar.triki@enis.tn"
    MAIL_DEFAULT_SENDER = 'omar.triki@enis.tn'
    MAIL_PASSWORD = "Saharwindows@+=1996"


class ConfigWithMailPort(Config):
    MAIL_SERVER = 'sandbox.smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME = '19a5b5ea2fc71d'
    MAIL_PASSWORD = 'd55b3b4a5703bf'
    MAIL_DEFAULT_SENDER = '19a5b5ea2fc71d'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False


app = Flask(__name__)
app.config.update(
    SECRET_KEY='helloworldrgpujefpeogzemogkn',
    SQLALCHEMY_DATABASE_URI='sqlite:///project.db',
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='omar.triki@enis.th',
    MAIL_PASSWORD='Omar@+=1996'
)
mail = Mail(app=app)
login_manager = LoginManager(app=app)
login_manager.login_view = '/login'
db = SQLAlchemy(app=app)
DOMAIN = 'https://dev-r2k0w0yq8vtxnpz2.us.auth0.com'
CLIEND_ID = 'BFE24WXxoiEzF5qiass44LLOIoShYhfr'
CLIENT_SECRET = 'cFJ6lbxBz-Xegct1SvR434NMNXyZI9myl-jxxzqAJvRrLxQMoSJUz6JnlLsWa_qJ'
