"""
Configuration Module

Centralized configuration management for the application.
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "data", "clawtrader.db")}'
    )
    
    POSTGRESQL_URL = os.getenv('POSTGRESQL_URL')
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    PORT = int(os.getenv('PORT', 8001))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    ALLOWED_ORIGINS = os.getenv(
        'ALLOWED_ORIGINS',
        'https://trading-agent-for-dscourse.surge.sh,http://localhost:8080'
    ).split(',')
    
    TOKEN_EXPIRE_DAYS = int(os.getenv('TOKEN_EXPIRE_DAYS', 30))
    
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 10))
    DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 20))
    DB_POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', 3600))
    
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def is_development(self) -> bool:
        return self.FLASK_ENV == 'development'
    
    @property
    def is_production(self) -> bool:
        return self.FLASK_ENV == 'production'
    
    @property
    def is_postgresql(self) -> bool:
        return self.DATABASE_URL.startswith('postgresql')


settings = Settings()
