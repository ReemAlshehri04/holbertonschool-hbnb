from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from config import config  # استيراد قاموس الإعدادات من ملف config.py

# تعريف كائن SQLAlchemy خارج create_app لمنع المشاكل
db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # 1. تحميل الإعدادات من ملف config.py (ضروري جداً للدرجة الكاملة)
    app.config.from_object(config[config_name])

    # 2. ربط SQLAlchemy بالتطبيق
    db.init_app(app)

    api = Api(app, version='1.0', title='HBnB API',
              description='HBnB Application API', doc='/api/v1/')

    # استيراد الـ Namespaces
    from app.api.v1.users import api as users_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.auth import api as auth_ns # لا تنسي الـ auth إذا أضفتيه سابقاً

    # تسجيل الـ Namespaces
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(auth_ns, path='/api/v1/auth')

    return app