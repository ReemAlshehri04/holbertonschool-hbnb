#!/usr/bin/python3
from repository.repository import InMemoryRepository
from models.user import User


class HBnBFacade:

    def __init__(self):
        self.user_repository = InMemoryRepository()

    # CREATE
    def create_user(self, data):
        if self.user_repository.get_by_attribute("email", data["email"]):
            raise ValueError("Email already exists")

        user = User(
            data["first_name"],
            data["last_name"],
            data["email"],
            data["password"]
        )

        return self.user_repository.add(user)

    # GET ONE
    def get_user(self, user_id):
        return self.user_repository.get(user_id)

    # GET ALL
    def get_all_users(self):
        return self.user_repository.get_all()

    # UPDATE
    def update_user(self, user_id, data):
        return self.user_repository.update(user_id, data)
