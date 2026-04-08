from flask import request
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade
import re

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'id': fields.String(readOnly=True),
    'first_name': fields.String(required=True, min_length=1, max_length=50),
    'last_name': fields.String(required=True, min_length=1, max_length=50),
    'email': fields.String(required=True)
})

user_input_model = api.model('UserInput', {
    'first_name': fields.String(required=True, min_length=1, max_length=50),
    'last_name':  fields.String(required=True, min_length=1, max_length=50),
    'email':      fields.String(required=True),
    'password':   fields.String(required=True),
})

def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email) is not None

@api.route('/')
class UserList(Resource):

    @jwt_required()
    @api.marshal_list_with(user_model)
    def get(self):
        """List all users (Admin/Authenticated only)"""
        return facade.get_all_users(), 200

    @api.expect(user_input_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Invalid input or Email already exists')
    def post(self):
        """Register a new user (Public Registration)"""
        user_data = api.payload

        # 1. التحقق من صحة الإيميل
        if not is_valid_email(user_data['email']):
            abort(400, "Invalid email format")

        # 2. التأكد من أن الإيميل غير مسجل مسبقاً
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            abort(400, "Email already registered")

        # 3. إنشاء المستخدم
        try:
            new_user = facade.create_user(user_data)
            # تم إزالة شرط الـ Admin للسماح لكِ بالإنشاء عبر التيرمينال
            return {
                'id': new_user.id,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'email': new_user.email
            }, 201
        except Exception as e:
            abort(400, str(e))

@api.route('/<user_id>')
@api.param('user_id', 'The user identifier')
@api.response(404, 'User not found')
class UserResource(Resource):

    @api.marshal_with(user_model)
    def get(self, user_id):
        user = facade.get_user(user_id)
        if not user:
            abort(404, "User not found")
        return user, 200

    @jwt_required()
    @api.expect(user_model, validate=False)
    @api.response(200, 'User updated successfully')
    @api.response(400, 'Invalid data')
    @api.response(403, 'Admin privileges required')
    def put(self, user_id):
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        if str(user_id) != str(current_user_id) and not is_admin:
            abort(403, "Admin privileges required")

        user_data = api.payload or {}

        if 'email' in user_data:
            existing_user = facade.get_user_by_email(user_data['email'])
            if existing_user and str(existing_user.id) != str(user_id):
                abort(400, "Email already exists")

        if not is_admin and ('email' in user_data or 'password' in user_data):
             abort(400, "You cannot modify email or password.")

        updated_user = facade.update_user(user_id, user_data)
        if not updated_user:
            abort(404, "User not found")

        return {
                'id': updated_user.id,
                'first_name': updated_user.first_name,
                'last_name': updated_user.last_name,
                'email': updated_user.email
            }, 200