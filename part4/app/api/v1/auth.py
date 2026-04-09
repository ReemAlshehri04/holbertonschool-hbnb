from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from app.services import facade

api = Namespace('auth', description='Authentication operations')

# نموذج تسجيل الدخول
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

# نموذج تسجيل مستخدم جديد
register_model = api.model('Register', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name')
})

# نموذج معلومات المستخدم
user_model = api.model('User', {
    'id': fields.String(description='User ID'),
    'email': fields.String(description='User email'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name')
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    @api.response(200, 'Login successful')
    @api.response(400, 'Email and password are required')
    @api.response(401, 'Invalid credentials')
    def post(self):
        """تسجيل الدخول والحصول على JWT tokens"""
        credentials = api.payload or request.get_json() or {}

        email = credentials.get('email')
        password = credentials.get('password')

        if not email or not password:
            return {'error': 'Email and password are required'}, 400

        user = facade.get_user_by_email(email)

        if not user or not user.verify_password(password):
            return {'error': 'Invalid credentials'}, 401

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, 200

@api.route('/register')
class Register(Resource):
    @api.expect(register_model)
    @api.response(201, 'User created successfully')
    @api.response(400, 'Invalid input data')
    @api.response(409, 'User already exists')
    def post(self):
        """تسجيل مستخدم جديد"""
        data = api.payload or request.get_json() or {}
        
        # التحقق من وجود جميع الحقول المطلوبة
        required_fields = ['email', 'password', 'first_name', 'last_name']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return {
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, 400
        
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        # التحقق من صحة البريد الإلكتروني
        if '@' not in email or '.' not in email:
            return {'error': 'Invalid email format'}, 400
        
        # التحقق من طول كلمة المرور
        if len(password) < 6:
            return {'error': 'Password must be at least 6 characters long'}, 400
        
        try:
            # التحقق إذا كان المستخدم موجود بالفعل
            existing_user = facade.get_user_by_email(email)
            if existing_user:
                return {'error': 'User with this email already exists'}, 409
            
            # إنشاء مستخدم جديد
            user_data = {
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name
            }
            
            new_user = facade.create_user(user_data)
            
            return {
                'message': 'User created successfully',
                'user': {
                    'id': str(new_user.id),
                    'email': new_user.email,
                    'first_name': new_user.first_name,
                    'last_name': new_user.last_name
                }
            }, 201
            
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': 'Internal server error'}, 500

@api.route('/profile')
class UserProfile(Resource):
    @jwt_required()
    @api.response(200, 'Success', user_model)
    @api.response(401, 'Unauthorized')
    @api.response(404, 'User not found')
    def get(self):
        """الحصول على معلومات المستخدم الحالي (يتطلب توكن)"""
        try:
            user_id = get_jwt_identity()
            user = facade.get_user(user_id)
            
            if not user:
                return {'error': 'User not found'}, 404
            
            return {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }, 200
            
        except Exception as e:
            return {'error': 'Internal server error'}, 500

@api.route('/refresh')
class RefreshToken(Resource):
    @jwt_required(refresh=True)
    @api.response(200, 'Token refreshed successfully')
    @api.response(401, 'Unauthorized')
    def post(self):
        """تحديث access token باستخدام refresh token"""
        try:
            current_user_id = get_jwt_identity()
            new_access_token = create_access_token(identity=current_user_id)
            
            return {
                'access_token': new_access_token
            }, 200
            
        except Exception as e:
            return {'error': 'Failed to refresh token'}, 401