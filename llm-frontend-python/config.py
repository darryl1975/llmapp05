import os

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8080')
FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))
DEBUG = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
