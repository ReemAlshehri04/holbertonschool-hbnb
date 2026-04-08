from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from app.services import facade

api = Namespace('auth', description='Authentication operations')

login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

token_model = api.model('Token', {
    'access_token': fields.String(description='JWT access token'),
    'refresh_token': fields.String(description='JWT refresh token')
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """Authenticate user and return a JWT access token and refresh token"""
        credentials = api.payload or {}
        email = credentials.get('email')
        password = credentials.get('password')

        if not email or not password:
            return {'error': 'Email and password are required'}, 400

        user = facade.get_user_by_email(email)
        if not user or not user.verify_password(password):
            return {'error': 'Invalid credentials'}, 401

        identity = str(user.id)
        
       
        additional_claims = {"is_admin": True}

        access_token = create_access_token(identity=identity, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=identity)

        return {'access_token': access_token, 'refresh_token': refresh_token}, 200

@api.route('/refresh')
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """Exchange a valid refresh token for a new access token"""
        current_user = get_jwt_identity()
        user = facade.get_user(current_user)
        if not user:
            return {'error': 'User not found'}, 404

       
        additional_claims = {"is_admin": True}
        
        new_access = create_access_token(identity=str(current_user), additional_claims=additional_claims)
        return {'access_token': new_access}, 200

@api.route('/me')
class Me(Resource):
    @jwt_required()
    def get(self):
        """Return the authenticated user's basic profile"""
        current_user = get_jwt_identity()
        user = facade.get_user(current_user)
        if not user:
            return {'error': 'User not found'}, 404

        return {
            'id': str(user.id),
            'first_name': getattr(user, 'first_name', None),
            'last_name': getattr(user, 'last_name', None),
            'email': getattr(user, 'email', None),
            'is_admin': True 
        }, 200