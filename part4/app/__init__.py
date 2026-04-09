# app/__init__.py
from flask import Flask
from flask_restx import Api
from flask_cors import CORS

# ✅ استيراد الـ extensions من ملف واحد
from app.extensions import db, bcrypt, jwt

def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ✅ ربط الـ extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # ✅ إعداد CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # ✅ إعداد API
    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        doc='/api/v1/'
    )

    # ✅ إضافة الـ namespaces
    from app.api.v1.auth import api as auth_ns
    api.add_namespace(auth_ns, path='/api/v1/auth')

    from app.api.v1.places import api as places_ns
    api.add_namespace(places_ns, path='/api/v1/places')

    return app