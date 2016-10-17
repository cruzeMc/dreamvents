from app import views
from app import *
from flask_compress import Compress

compress = Compress()

if __name__ == '__main__':
    compress.init_app(app)
    app.run(debug=True, host='0.0.0.0', port=8082, threaded=True, use_reloader=True)