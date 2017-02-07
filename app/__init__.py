from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_mail import Mail, Message
import flask_sijax
import os
import uuid
from flask_compress import Compress

UPLOAD_FOLDER = 'app/static/profile_pics'
WORE_WHAT = 'app/static/wore_what'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')

app = Flask(__name__)

app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500
Compress(app)

app.config['SIJAX_STATIC_PATH'] = path
app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
flask_sijax.Sijax(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://dreamvents:Naruto123?@localhost:5432/capstone'


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['WORE_WHAT'] = WORE_WHAT

app.config['MIDDLEWARE_CLASSES '] = ('htmlmin.middleware.HtmlMinifyMiddleware','htmlmin.middleware.MarkRequestMiddleware',)
app.config['HTML_MINIFY'] = True

app.config['TEMPLATES_AUTO_RELOAD'] = True

app.config.from_object('config')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


app.secret_key = str(uuid.uuid4())
app.config['SESSION_TYPE'] = 'filesystem'

sess = Session()
sess.init_app(app)

mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'cruze.mcfarlane@gmail.com'
app.config['MAIL_PASSWORD'] = 'gtgxugkvzqjcgeje'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
# mail.init_app(app)

app.jinja_env.add_extension('jinja2.ext.do')
