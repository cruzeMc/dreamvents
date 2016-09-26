from app import views
from app import *

if __name__== '__main__':
    app.run(debug=True, host='0.0.0.0', port=8082, threaded=True, use_reloader=True)