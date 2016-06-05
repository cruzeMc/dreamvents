import os

import psycopg2
import urlparse



WTF_CSRF_ENABLED = True
SECRET_KEY = 'capstoneproj'
SECURITY_REGISTRABLE = True

#SQLALCHEMY_DATABASE_URI='postgresql://capstoneproject:success@localhost/capstonedb'
SQLALCHEMY_DATABASE_URI='postgres://dreamvents:Naruto123?@localhost:5432/capstone'