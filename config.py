WTF_CSRF_ENABLED = True
SECRET_KEY = 'capstoneproj'

#SQLALCHEMY_DATABASE_URI='postgresql://capstoneproject:success@localhost/capstonedb'
SQLALCHEMY_DATABASE_URI='postgres://dreamvents:Naruto123?@localhost:5432/capstone'

SQLALCHEMY_TRACK_MODIFICATIONS = False

COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
COMPRESS_LEVEL = 6
COMPRESS_MIN_SIZE = 500

MIDDLEWARE_CLASSES = (
    # other middleware classes
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
)

HTML_MINIFY = True

#Pagination
FRIENDS_PER_PAGE = 20
EVENTS_PER_PAGE = 12
IMAGES_PER_PAGE = 20
VIDEOS_PER_PAGE = 20
