#!/usr/bin/python3
from flask import request
from flask_restx import Namespace, Resource, fields
from services.facade import HBnBFacade

api = Namespace('users', description='User operations')

facade = HBnBFacade()

user_model = api.model('User', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

update_model = api.model('UserUpdate', {
    'first_name': fields.String,
    'last_name': fields.String,
    'email': fields.String
})


@api.route('/')
class UserList(Resource):

    @api.expect(user_model)
    def post(self):
        data = request.json

        if not data:
            return {"error": "No input data provided"}, 400

        try:
            user = facade.create_user(data)
            return user.to_dict(), 201
        except ValueError as e:
            return {"error": str(e)}, 400

    def get(self):
        users = facade.get_all_users()
        return [user.to_dict() for user in users], 200


@api.route('/<string:user_id>')
class UserResource(Resource):

    def get(self, user_id):
        user = facade.get_user(user_id)

        if not user:
            return {"error": "User not found"}, 404

        return user.to_dict(), 200

    @api.expect(update_model)
    def put(self, user_id):
        data = request.json

        if not data:
            return {"error": "No input data provided"}, 400

        user = facade.update_user(user_id, data)

        if not user:
            return {"error": "User not found"}, 404

        return user.to_dict(), 200
