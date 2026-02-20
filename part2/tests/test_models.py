"""Unit tests for Business Logic models."""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.base_model import BaseModel
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review


class TestBaseModel(unittest.TestCase):
    """Tests for BaseModel."""

    def setUp(self):
        self.model = BaseModel()

    def test_id_is_string(self):
        self.assertIsInstance(self.model.id, str)

    def test_id_is_unique(self):
        model2 = BaseModel()
        self.assertNotEqual(self.model.id, model2.id)

    def test_created_at_set(self):
        self.assertIsNotNone(self.model.created_at)

    def test_updated_at_set(self):
        self.assertIsNotNone(self.model.updated_at)

    def test_save_updates_timestamp(self):
        old = self.model.updated_at
        import time; time.sleep(0.01)
        self.model.save()
        self.assertGreater(self.model.updated_at, old)

    def test_update_changes_attribute(self):
        self.model.name = 'test'
        self.model.update({'name': 'updated'})
        self.assertEqual(self.model.name, 'updated')

    def test_update_cannot_change_id(self):
        original_id = self.model.id
        self.model.update({'id': 'new-id'})
        self.assertEqual(self.model.id, original_id)

    def test_update_cannot_change_created_at(self):
        original = self.model.created_at
        self.model.update({'created_at': 'never'})
        self.assertEqual(self.model.created_at, original)


class TestUser(unittest.TestCase):
    """Tests for User model."""

    def setUp(self):
        self.user = User('John', 'Doe', 'john@example.com', 'secret')

    def test_attributes_set(self):
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'john@example.com')

    def test_is_admin_defaults_false(self):
        self.assertFalse(self.user.is_admin)

    def test_to_dict_no_password(self):
        d = self.user.to_dict()
        self.assertNotIn('password', d)

    def test_to_dict_has_required_keys(self):
        d = self.user.to_dict()
        for key in ('id', 'first_name', 'last_name', 'email',
                    'created_at', 'updated_at'):
            self.assertIn(key, d)

    def test_validate_email_valid(self):
        self.assertTrue(User.validate_email('test@example.com'))

    def test_validate_email_invalid(self):
        self.assertFalse(User.validate_email('notanemail'))
        self.assertFalse(User.validate_email('missing@'))
        self.assertFalse(User.validate_email('@nodomain.com'))


class TestAmenity(unittest.TestCase):
    """Tests for Amenity model."""

    def setUp(self):
        self.amenity = Amenity('WiFi')

    def test_name_set(self):
        self.assertEqual(self.amenity.name, 'WiFi')

    def test_to_dict_has_keys(self):
        d = self.amenity.to_dict()
        for key in ('id', 'name', 'created_at', 'updated_at'):
            self.assertIn(key, d)


class TestPlace(unittest.TestCase):
    """Tests for Place model."""

    def setUp(self):
        self.place = Place('Beach House', 'Nice', 100.0, 36.7, 3.0, 'owner-1')

    def test_attributes_set(self):
        self.assertEqual(self.place.title, 'Beach House')
        self.assertEqual(self.place.price, 100.0)
        self.assertEqual(self.place.latitude, 36.7)
        self.assertEqual(self.place.longitude, 3.0)
        self.assertEqual(self.place.owner_id, 'owner-1')

    def test_amenities_list_empty(self):
        self.assertEqual(self.place.amenities, [])

    def test_reviews_list_empty(self):
        self.assertEqual(self.place.reviews, [])

    def test_to_dict_has_keys(self):
        d = self.place.to_dict()
        for key in ('id', 'title', 'description', 'price',
                    'latitude', 'longitude', 'owner_id',
                    'created_at', 'updated_at'):
            self.assertIn(key, d)


class TestReview(unittest.TestCase):
    """Tests for Review model."""

    def setUp(self):
        self.review = Review('Great!', 5, 'place-1', 'user-1')

    def test_attributes_set(self):
        self.assertEqual(self.review.text, 'Great!')
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.place_id, 'place-1')
        self.assertEqual(self.review.user_id, 'user-1')

    def test_to_dict_has_keys(self):
        d = self.review.to_dict()
        for key in ('id', 'text', 'rating', 'place_id', 'user_id',
                    'created_at', 'updated_at'):
            self.assertIn(key, d)


if __name__ == '__main__':
    unittest.main()
