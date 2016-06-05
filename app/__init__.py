from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import flask_sijax
import os
import uuid

UPLOAD_FOLDER = 'app/static/profile_pics'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')

app = Flask(__name__)
app.config['SIJAX_STATIC_PATH'] = path
app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
flask_sijax.Sijax(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://dreamvents:Naruto123?@localhost:5432/capstone'
app.config['SECURITY_KEY'] = str(uuid.uuid4())
app.config['SECURITY_REGISTRABLE'] = True
app.config['SECURITY_LOGIN_URL'] = '/secretive_login'
app.config['SECURITY_POST_LOGIN'] = '/profile'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SOCIAL_FACEBOOK'] = {
    'consumer_key': '292474344420257',
    'consumer_secret': 'f2e520ad1cf41cfab65005cb34bd2bb8'
}
app.config['SOCIAL_GOOGLE'] = {
    'consumer_key': 'xxx',
    'consumer_secret': 'xxx'
}
app.config.from_object('config')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


app.secret_key = str(uuid.uuid4())
app.config['SESSION_TYPE'] = 'filesystem'

sess = Session()
sess.init_app(app)

app.jinja_env.add_extension('jinja2.ext.do')
