import os
from datetime import timedelta

# تحديد مجلد المشروع الأساسي لضمان إنشاء قاعدة البيانات في المكان الصحيح
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False

    # إعدادات SQLAlchemy المطلوبة للتقييم
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # القيمة الافتراضية العامة
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'development.db')
    )

    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_HOURS', '1')))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_DAYS', '7')))
    JWT_ACCESS_TOKEN_EXPIRES_DISABLE = os.getenv('JWT_ACCESS_EXPIRES_DISABLE', 'false').lower() == 'true'


class DevelopmentConfig(Config):
    DEBUG = True
    # إجبار نسخة التطوير على استخدام نفس اسم الملف لسهولة الفحص
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'development.db')
    )


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}