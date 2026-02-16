#!/usr/bin/python3
from abc import ABC, abstractmethod


class Repository(ABC):

    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, obj_id, data):
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, value):
        pass


class InMemoryRepository(Repository):

    def __init__(self):
        self._storage = {}

    def add(self, obj):
        self._storage[obj.id] = obj
        return obj

    def get(self, obj_id):
        return self._storage.get(obj_id)

    def get_all(self):
        return list(self._storage.values())

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if not obj:
            return None

        for key, value in data.items():
            if hasattr(obj, key) and key != "id":
                setattr(obj, key, value)

        return obj

    def get_by_attribute(self, attr_name, value):
        return next(
            (obj for obj in self._storage.values()
             if getattr(obj, attr_name, None) == value),
            None
        )
