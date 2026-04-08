from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('reviews', description='Review operations')

review_model = api.model('Review', {
    'text':     fields.String(required=True),
    'rating':   fields.Integer(required=True),
    'user_id':  fields.String(required=False),
    'place_id': fields.String(required=True),
})


@api.route('/')
class ReviewList(Resource):

    def get(self):
        """Get all reviews"""
        return [r.to_dict() for r in facade.get_all_reviews()], 200

    @jwt_required()
    @api.expect(review_model, validate=True)
    def post(self):
        """Create a new review"""
        current_user = get_jwt_identity()
        data = api.payload or {}

        place_id = data.get('place_id')
        if not place_id:
            return {'error': 'place_id required'}, 400

        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        if str(getattr(place, 'owner_id', None)) == str(current_user):
            return {'error': 'You cannot review your own place.'}, 400

        existing = facade.get_review_by_user_and_place(user_id=current_user, place_id=place_id)
        if existing:
            return {'error': 'You have already reviewed this place.'}, 400

        data['user_id'] = str(current_user)

        try:
            review = facade.create_review(data)
            return review.to_dict(), 201
        except ValueError as e:
            return {'error': str(e)}, 400


@api.route('/<string:review_id>')
class ReviewResource(Resource):

    def get(self, review_id):
        """Get a review by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return review.to_dict(), 200

    @jwt_required()
    @api.expect(review_model, validate=False)
    def put(self, review_id):
        """Update a review - author or admin"""
        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        data = api.payload or {}

        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        # Admin bypasses ownership check
        if not is_admin and str(getattr(review, 'user_id', None)) != str(current_user):
            return {'error': 'Unauthorized action'}, 403

        data.pop('user_id', None)
        data.pop('place_id', None)

        try:
            updated = facade.update_review(review_id, data)
            if not updated:
                return {'error': 'Review not found'}, 404
            return updated.to_dict(), 200
        except ValueError as e:
            return {'error': str(e)}, 400

    @jwt_required()
    def delete(self, review_id):
        """Delete a review - author or admin"""
        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        # Admin bypasses ownership check
        if not is_admin and str(getattr(review, 'user_id', None)) != str(current_user):
            return {'error': 'Unauthorized action'}, 403

        if not facade.delete_review(review_id):
            return {'error': 'Review not found'}, 404
        return {'message': 'Review deleted successfully'}, 200
