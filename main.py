import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.join(BASE_DIR, 'server')

sys.path.insert(0, SERVER_DIR)

os.chdir(SERVER_DIR)

from simple_server import app, init_db

init_db()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8001)))
