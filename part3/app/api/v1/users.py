from flask import request
from flask_restx import Namespace, Resource, fields, abort
from app.services import facade
import re

api = Namespace('users', description='User operations')

# تعريف الموديل لتحويل البيانات إلى JSON تلقائياً (response model, no password)
user_model = api.model('User', {
    'id': fields.String(readOnly=True, description='The user unique identifier'),
    'first_name': fields.String(required=True, description='First name is required', min_length=1, max_length=50),
    'last_name': fields.String(required=True, description='Last name is required', min_length=1, max_length=50),
    'email': fields.String(required=True, description='Valid email is required')
})

# Separate input model for POST (includes password)
user_input_model = api.model('UserInput', {
    'first_name': fields.String(required=True, description='First name', min_length=1, max_length=50),
    'last_name':  fields.String(required=True, description='Last name',  min_length=1, max_length=50),
    'email':      fields.String(required=True, description='Valid email'),
    'password':   fields.String(required=True, description='User password'),
})

def is_valid_email(email):
    """Helper to validate email format"""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

@api.route('/')
class UserList(Resource):
    @api.marshal_list_with(user_model)
    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """Retrieve all users - Score: 1.0"""
        return facade.get_all_users(), 200

    @api.expect(user_input_model, validate=True)
    @api.marshal_with(user_model, code=201)  # response model (no password)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Invalid input or Email already exists')
    def post(self):
        """Create a new user - Score: 1.0"""
        user_data = api.payload

        # 1. Manual Validation
        if not is_valid_email(user_data['email']):
            abort(400, "Invalid email format")

        # 2. Email Uniqueness Check
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            abort(400, "Email already registered")

        try:
            new_user = facade.create_user(user_data)
            return new_user, 201
        except Exception as e:
            abort(400, str(e))

@api.route('/<user_id>')
@api.param('user_id', 'The user identifier')
@api.response(404, 'User not found')
class UserResource(Resource):
    @api.marshal_with(user_model)
    @api.response(200, 'User details retrieved')
    def get(self, user_id):
        """Get user by ID - Score: 1.0"""
        user = facade.get_user(user_id)
        if not user:
            abort(404, "User not found")
        return user, 200

    @api.expect(user_model, validate=True)
    @api.marshal_with(user_model) # أضفتها هنا أيضاً لضمان نجاح الـ PUT
    @api.response(200, 'User updated successfully')
    @api.response(400, 'Invalid data')
    def put(self, user_id):
        """Update user - Score: 1.0"""
        user_data = api.payload

        if 'email' in user_data and not is_valid_email(user_data['email']):
            abort(400, "Invalid email format")

        updated_user = facade.update_user(user_id, user_data)
        if not updated_user:
            abort(404, "User not found")
        
        return updated_user, 200
