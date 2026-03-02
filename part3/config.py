import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False

    # Part 3 additions
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///app.db'  # placeholder for now
    )
    JWT_SECRET_KEY = os.getenv(
        'JWT_SECRET_KEY',
        'default_jwt_secret_key'
    )


class DevelopmentConfig(Config):
    DEBUG = True
    # Optional: override DB for local dev
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL',
        'sqlite:///dev.db'
    )


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
