from flask_restx import Namespace, Resource, fields
from flask import request
from app.services import facade

api = Namespace('places', description='Place operations')

# Serializer / input model
place_model = api.model('Place', {
    'title': fields.String(required=True),
    'description': fields.String(required=True),
    'price': fields.Float(required=True),
    'latitude': fields.Float(required=True),
    'longitude': fields.Float(required=True),
    'owner_id': fields.String(required=True),
    'amenities': fields.List(fields.String, required=False)
})

# Serializer for output (includes id + timestamps)
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
    @api.marshal_list_with(place_response)
    def get(self):
        """Get all places"""
        return facade.get_all_places()

    @api.expect(place_model)
    @api.marshal_with(place_response, code=201)
    def post(self):
        """Create a new place"""
        data = request.get_json()
        return facade.create_place(data), 201


@api.route('/<string:place_id>')
class PlaceResource(Resource):
    @api.marshal_with(place_response)
    def get(self, place_id):
        """Get a place by ID"""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, "Place not found")
        return place

    @api.expect(place_model)
    @api.marshal_with(place_response)
    def put(self, place_id):
        """Update a place"""
        data = request.get_json()
        updated = facade.update_place(place_id, data)
        if not updated:
            api.abort(404, "Place not found")
        return updated
