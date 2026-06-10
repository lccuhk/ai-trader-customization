import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, 'data', 'clawtrader.db')
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DEFAULT_DB_PATH}')

def create_db_engine():
    if DATABASE_URL.startswith('postgresql'):
        engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
            pool_pre_ping=True,
            pool_use_lifo=True,
            echo=False
        )
    else:
        engine = create_engine(
            DATABASE_URL,
            connect_args={'check_same_thread': False},
            echo=False
        )
    return engine

engine = create_db_engine()

SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    return SessionLocal()

def _column_exists(engine, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table using PRAGMA."""
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(f"PRAGMA table_info({table_name})")
            ).fetchall()
            return any(row[1] == column_name for row in result)
    except Exception:
        return False


def _add_column(engine, table_name: str, column_def: str):
    """Add a column to an existing table."""
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_def}"))
            conn.commit()
    except Exception as e:
        print(f"  ⚠️  Could not add column to {table_name}: {e}")


def repair_schema():
    """
    Repair database schema that might have been created by simple_server.py
    with an incomplete schema (missing columns like username, display_name).

    SQLAlchemy's create_all() does NOT add missing columns to existing tables,
    so we need to explicitly add them.
    """
    # === users table: may be missing username, display_name ===
    if _column_exists(engine, 'users', 'id'):
        if not _column_exists(engine, 'users', 'username'):
            print("  🔧 Adding missing column: users.username")
            _add_column(engine, 'users', 'username VARCHAR(50) UNIQUE')
        if not _column_exists(engine, 'users', 'display_name'):
            print("  🔧 Adding missing column: users.display_name")
            _add_column(engine, 'users', 'display_name VARCHAR(100)')

    # === user_stats table: may be missing losing_trades, max_drawdown, etc. ===
    if _column_exists(engine, 'user_stats', 'id'):
        if not _column_exists(engine, 'user_stats', 'losing_trades'):
            _add_column(engine, 'user_stats', 'losing_trades INTEGER DEFAULT 0')
        if not _column_exists(engine, 'user_stats', 'max_drawdown'):
            _add_column(engine, 'user_stats', 'max_drawdown FLOAT DEFAULT 0.0')
        if not _column_exists(engine, 'user_stats', 'avg_win'):
            _add_column(engine, 'user_stats', 'avg_win FLOAT DEFAULT 0.0')
        if not _column_exists(engine, 'user_stats', 'avg_loss'):
            _add_column(engine, 'user_stats', 'avg_loss FLOAT DEFAULT 0.0')
        if not _column_exists(engine, 'user_stats', 'profit_factor'):
            _add_column(engine, 'user_stats', 'profit_factor FLOAT DEFAULT 0.0')


def init_db():
    from models import Base
    Base.metadata.create_all(bind=engine)
    repair_schema()
