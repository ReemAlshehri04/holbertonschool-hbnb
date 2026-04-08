from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity', min_length=1)
})

amenity_response_model = api.clone('AmenityResponse', amenity_model, {
    'id': fields.String(readOnly=True),
    'created_at': fields.String(readOnly=True),
    'updated_at': fields.String(readOnly=True)
})


@api.route('/')
class AmenityList(Resource):

    @api.marshal_list_with(amenity_response_model)
    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """Retrieve all amenities"""
        return facade.get_all_amenities(), 200

    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    def post(self):
        """Create a new amenity - Admin only"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            abort(403, "Admin privileges required")

        try:
            new_amenity = facade.create_amenity(api.payload)
            return new_amenity.to_dict(), 201
        except Exception as e:
            abort(400, str(e))


@api.route('/<amenity_id>')
@api.param('amenity_id', 'The amenity identifier')
@api.response(404, 'Amenity not found')
class AmenityResource(Resource):

    @api.marshal_with(amenity_response_model)
    def get(self, amenity_id):
        """Get amenity by ID"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            abort(404, "Amenity not found")
        return amenity, 200

    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.response(200, 'Amenity updated successfully')
    @api.response(403, 'Admin privileges required')
    def put(self, amenity_id):
        """Update an amenity - Admin only"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            abort(403, "Admin privileges required")

        existing = facade.get_amenity(amenity_id)
        if not existing:
            abort(404, "Amenity not found")

        updated = facade.update_amenity(amenity_id, api.payload)
        if not updated:
            abort(404, "Amenity not found")
        return updated.to_dict(), 200
