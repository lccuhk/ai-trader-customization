import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.join(BASE_DIR, 'server')

sys.path.insert(0, SERVER_DIR)

os.chdir(SERVER_DIR)

from app import app, init_db
from config import settings

init_db()

if __name__ == '__main__':
    print(f"Starting server on {settings.HOST}:{settings.PORT}")
    print(f"Environment: {settings.FLASK_ENV}")
    print(f"Database: {'PostgreSQL' if settings.is_postgresql else 'SQLite'}")
    print(f"Debug: {settings.FLASK_DEBUG}")
    
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.FLASK_DEBUG
    )
