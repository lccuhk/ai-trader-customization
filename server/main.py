from app import app, init_db

init_db()

if __name__ == '__main__':
    from config import settings
    app.run(host='0.0.0.0', port=settings.PORT, debug=False)
