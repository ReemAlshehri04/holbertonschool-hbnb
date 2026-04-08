# app/api/v1/__init__.py
from flask_restx import Namespace
from .auth import api as auth_ns
from .places import api as places_ns
from .reviews import api as reviews_ns
from .users import api as users_ns
from .amenities import api as amenities_ns  

# Export a list so the app factory can register them
namespaces = [
    ('/auth', auth_ns),
    ('/places', places_ns),
    ('/reviews', reviews_ns),
    ('/users', users_ns),
    ('/amenities', amenities_ns),
]
