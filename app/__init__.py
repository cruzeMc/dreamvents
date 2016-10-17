from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import flask_sijax
import os
import uuid
from flask_compress import Compress

UPLOAD_FOLDER = 'app/static/profile_pics'
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

app.config['SECURITY_KEY'] = str(uuid.uuid4())
app.config['SECURITY_REGISTRABLE'] = True
app.config['SECURITY_LOGIN_URL'] = '/secretive_login'
app.config['SECURITY_POST_LOGIN'] = '/profile'


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MIDDLEWARE_CLASSES '] = ('htmlmin.middleware.HtmlMinifyMiddleware','htmlmin.middleware.MarkRequestMiddleware',)
app.config['HTML_MINIFY'] = True

app.config['TEMPLATES_AUTO_RELOAD'] = True

app.config['SOCIAL_FACEBOOK'] = {
    'consumer_key': '1805263609731402',
    'consumer_secret': '182a766f168be71e2198407a666dfe60',
    'request_token_params': {
        'scope': ('public_profile '
                  'email')
                  # 'user_about_me '
                  # 'user_photos '
                  # 'user_events '
                  # 'rsvp_event '
                  # 'user_birthday')
    }
}
app.config['SOCIAL_TWITTER'] = {
    'consumer_key': 'gW5cEShbF1xNrXa7q0goChkUv',
    'consumer_secret': 'LY2cqjct2DemvX3y0JmIt0uNsv9EpzMApzThcpenEdJyOFHR7A'
}
app.config['INSTAGRAM'] = {
    'consumer_key': '88a81765abdd4079af6fd84ccad53efa',
    'consumer_secret': 'cfdf6e1d27414a429a24b49a355e244c',
    'secret_key': '',
    'redirect_uri': 'http://localhost:5000/instagram_callback'
}
app.config['SOCIAL_GOOGLE'] = {
    'consumer_key': '785048580168-i8n5vbijibl6f5s0j05116e1tur7hcfu.apps.googleusercontent.com',
    'consumer_secret': 'TcUdls4cZJsKMWZRjFTjRaMR',
    'request_token_params': {
        'scope': ('https://www.googleapis.com/auth/userinfo.profile '
                  'https://www.googleapis.com/auth/plus.me '
                  'https://www.googleapis.com/auth/userinfo.email')

    }
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
