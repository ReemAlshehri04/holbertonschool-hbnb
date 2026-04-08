from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('places', description='Place operations')

place_model = api.model('Place', {
    'title': fields.String(required=True),
    'description': fields.String(required=False),
    'price': fields.Float(required=True),
    'latitude': fields.Float(required=True),
    'longitude': fields.Float(required=True),
    'owner_id': fields.String(required=False),
    'amenities': fields.List(fields.String, required=False)
})

place_response = api.model('PlaceResponse', {
    'id': fields.String,
    'title': fields.String,
    'description': fields.String,
    'price': fields.Float,
    'latitude': fields.Float,
    'longitude': fields.Float,
    'owner_id': fields.String,
    'amenities': fields.List(fields.String),
    'created_at': fields.String,
    'updated_at': fields.String
})


@api.route('/')
class PlaceList(Resource):

    def get(self):
        """Get all places - public"""
        places = facade.get_all_places()
        return [p.to_dict() for p in places], 200

    @jwt_required()
    @api.expect(place_model)
    def post(self):
        """Create a new place"""
        current_user = get_jwt_identity()
        data = request.get_json() or {}
        data['owner_id'] = str(current_user)
        try:
            place = facade.create_place(data)
            return place.to_dict(), 201
        except ValueError as e:
            return {'error': str(e)}, 400


@api.route('/<string:place_id>')
class PlaceResource(Resource):

    def get(self, place_id):
        """Get a place by ID - public"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        d = place.to_dict()
        owner = facade.get_user(place.owner_id)
        if owner:
            d['owner'] = owner.to_dict()
        return d, 200

    @jwt_required()
    @api.expect(place_model)
    def put(self, place_id):
        """Update a place - owner or admin"""
        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        # Admin bypasses ownership check
        if not is_admin and str(getattr(place, 'owner_id', None)) != str(current_user):
            return {'error': 'Unauthorized action'}, 403

        data = request.get_json() or {}
        data.pop('owner_id', None)

        try:
            updated = facade.update_place(place_id, data)
            if not updated:
                return {'error': 'Place not found'}, 404
            return updated.to_dict(), 200
        except ValueError as e:
            return {'error': str(e)}, 400


@api.route('/<string:place_id>/reviews')
class PlaceReviews(Resource):

    def get(self, place_id):
        """Get all reviews for a place - public"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        reviews = facade.get_reviews_by_place(place_id)
        return [r.to_dict() for r in reviews], 200
