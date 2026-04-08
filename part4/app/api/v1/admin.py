from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt
from app.services import facade

api = Namespace('admin', description='Admin-only operations')

user_input_model = api.model('AdminUserInput', {
    'first_name': fields.String(required=True),
    'last_name':  fields.String(required=True),
    'email':      fields.String(required=True),
    'password':   fields.String(required=True),
    'is_admin':   fields.Boolean(required=False),
})

amenity_model = api.model('AdminAmenityInput', {
    'name': fields.String(required=True),
})


def require_admin():
    claims = get_jwt()
    if not claims.get('is_admin', False):
        abort(403, "Admin privileges required")


@api.route('/users')
class AdminUserList(Resource):

    @jwt_required()
    def post(self):
        """Admin: create a new user"""
        require_admin()
        data = api.payload or {}

        import re
        email = data.get('email', '')
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            abort(400, "Invalid email format")

        if facade.get_user_by_email(email):
            abort(400, "Email already registered")

        try:
            user = facade.create_user(data)
            return user.to_dict(), 201
        except Exception as e:
            abort(400, str(e))


@api.route('/users/<user_id>')
class AdminUserResource(Resource):

    @jwt_required()
    def put(self, user_id):
        """Admin: update any user (including email and password)"""
        require_admin()
        data = api.payload or {}

        # Check email uniqueness if changing email
        if 'email' in data:
            existing = facade.get_user_by_email(data['email'])
            if existing and str(existing.id) != str(user_id):
                abort(400, "Email already in use")

        user = facade.get_user(user_id)
        if not user:
            abort(404, "User not found")

        # Handle password hashing separately
        if 'password' in data:
            user.hash_password(data.pop('password'))

        user.update(data)
        facade.user_repo.db.session.commit()
        return user.to_dict(), 200

    @jwt_required()
    def delete(self, user_id):
        """Admin: delete any user"""
        require_admin()
        user = facade.get_user(user_id)
        if not user:
            abort(404, "User not found")
        facade.user_repo.delete(user_id)
        return {'message': 'User deleted successfully'}, 200


@api.route('/amenities')
class AdminAmenityList(Resource):

    @jwt_required()
    def post(self):
        """Admin: create a new amenity"""
        require_admin()
        try:
            amenity = facade.create_amenity(api.payload or {})
            return amenity.to_dict(), 201
        except Exception as e:
            abort(400, str(e))


@api.route('/amenities/<amenity_id>')
class AdminAmenityResource(Resource):

    @jwt_required()
    def put(self, amenity_id):
        """Admin: update an amenity"""
        require_admin()
        existing = facade.get_amenity(amenity_id)
        if not existing:
            abort(404, "Amenity not found")
        updated = facade.update_amenity(amenity_id, api.payload or {})
        return updated.to_dict(), 200
