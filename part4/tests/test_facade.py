"""Unit tests for HBnBFacade (services layer)."""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.facade import HBnBFacade


class TestFacadeUser(unittest.TestCase):
    """Tests for user operations in HBnBFacade."""

    def setUp(self):
        self.facade = HBnBFacade()

    def test_create_user_success(self):
        user = self.facade.create_user({
            'first_name': 'John', 'last_name': 'Doe',
            'email': 'john@example.com', 'password': '1234'
        })
        self.assertEqual(user.email, 'john@example.com')
        self.assertIsNotNone(user.id)

    def test_create_user_invalid_email(self):
        with self.assertRaises(ValueError):
            self.facade.create_user({
                'first_name': 'A', 'last_name': 'B',
                'email': 'notvalid', 'password': 'x'
            })

    def test_create_user_duplicate_email(self):
        data = {'first_name': 'A', 'last_name': 'B',
                'email': 'dup@example.com', 'password': 'x'}
        self.facade.create_user(data)
        with self.assertRaises(ValueError):
            self.facade.create_user(data)

    def test_get_user_returns_user(self):
        user = self.facade.create_user({
            'first_name': 'X', 'last_name': 'Y',
            'email': 'xy@example.com', 'password': 'p'
        })
        found = self.facade.get_user(user.id)
        self.assertEqual(found.id, user.id)

    def test_get_user_not_found(self):
        self.assertIsNone(self.facade.get_user('nonexistent'))

    def test_get_all_users(self):
        self.facade.create_user({
            'first_name': 'A', 'last_name': 'B',
            'email': 'a@test.com', 'password': 'p'
        })
        self.facade.create_user({
            'first_name': 'C', 'last_name': 'D',
            'email': 'c@test.com', 'password': 'p'
        })
        self.assertEqual(len(self.facade.get_all_users()), 2)

    def test_update_user(self):
        user = self.facade.create_user({
            'first_name': 'Old', 'last_name': 'Name',
            'email': 'upd@test.com', 'password': 'p'
        })
        updated = self.facade.update_user(user.id, {'first_name': 'New'})
        self.assertEqual(updated.first_name, 'New')

    def test_update_user_not_found(self):
        result = self.facade.update_user('nonexistent', {'first_name': 'X'})
        self.assertIsNone(result)

    def test_update_user_invalid_email(self):
        user = self.facade.create_user({
            'first_name': 'A', 'last_name': 'B',
            'email': 'valid@test.com', 'password': 'p'
        })
        with self.assertRaises(ValueError):
            self.facade.update_user(user.id, {'email': 'bademail'})

    def test_password_not_in_to_dict(self):
        user = self.facade.create_user({
            'first_name': 'A', 'last_name': 'B',
            'email': 'safe@test.com', 'password': 'secret'
        })
        self.assertNotIn('password', user.to_dict())


class TestFacadeAmenity(unittest.TestCase):
    """Tests for amenity operations in HBnBFacade."""

    def setUp(self):
        self.facade = HBnBFacade()

    def test_create_amenity_success(self):
        amenity = self.facade.create_amenity({'name': 'WiFi'})
        self.assertEqual(amenity.name, 'WiFi')
        self.assertIsNotNone(amenity.id)

    def test_create_amenity_empty_name(self):
        with self.assertRaises(ValueError):
            self.facade.create_amenity({'name': ''})

    def test_get_amenity(self):
        amenity = self.facade.create_amenity({'name': 'Pool'})
        found = self.facade.get_amenity(amenity.id)
        self.assertEqual(found.id, amenity.id)

    def test_get_amenity_not_found(self):
        self.assertIsNone(self.facade.get_amenity('nonexistent'))

    def test_get_all_amenities(self):
        self.facade.create_amenity({'name': 'WiFi'})
        self.facade.create_amenity({'name': 'Pool'})
        self.assertEqual(len(self.facade.get_all_amenities()), 2)

    def test_update_amenity(self):
        amenity = self.facade.create_amenity({'name': 'Old'})
        updated = self.facade.update_amenity(amenity.id, {'name': 'New'})
        self.assertEqual(updated.name, 'New')

    def test_update_amenity_not_found(self):
        self.assertIsNone(self.facade.update_amenity('nonexistent', {'name': 'x'}))


class TestFacadePlace(unittest.TestCase):
    """Tests for place operations in HBnBFacade."""

    def setUp(self):
        self.facade = HBnBFacade()
        self.user = self.facade.create_user({
            'first_name': 'Owner', 'last_name': 'User',
            'email': 'owner@test.com', 'password': 'p'
        })
        self.amenity = self.facade.create_amenity({'name': 'WiFi'})

    def _make_place(self, **kwargs):
        defaults = {
            'title': 'Beach House',
            'description': 'Nice place',
            'price': 100.0,
            'latitude': 36.7,
            'longitude': 3.0,
            'owner_id': self.user.id,
        }
        defaults.update(kwargs)
        return self.facade.create_place(defaults)

    def test_create_place_success(self):
        place = self._make_place()
        self.assertEqual(place.title, 'Beach House')
        self.assertEqual(place.owner_id, self.user.id)

    def test_create_place_with_amenities(self):
        place = self._make_place(amenities=[self.amenity.id])
        self.assertEqual(len(place.amenities), 1)
        self.assertEqual(place.amenities[0].id, self.amenity.id)

    def test_create_place_invalid_owner(self):
        with self.assertRaises(ValueError):
            self._make_place(owner_id='nonexistent')

    def test_create_place_negative_price(self):
        with self.assertRaises(ValueError):
            self._make_place(price=-1)

    def test_create_place_invalid_latitude_high(self):
        with self.assertRaises(ValueError):
            self._make_place(latitude=91)

    def test_create_place_invalid_latitude_low(self):
        with self.assertRaises(ValueError):
            self._make_place(latitude=-91)

    def test_create_place_invalid_longitude_high(self):
        with self.assertRaises(ValueError):
            self._make_place(longitude=181)

    def test_create_place_invalid_longitude_low(self):
        with self.assertRaises(ValueError):
            self._make_place(longitude=-181)

    def test_get_place(self):
        place = self._make_place()
        found = self.facade.get_place(place.id)
        self.assertEqual(found.id, place.id)

    def test_get_place_not_found(self):
        self.assertIsNone(self.facade.get_place('nonexistent'))

    def test_get_all_places(self):
        self._make_place()
        self._make_place(title='Mountain House')
        self.assertEqual(len(self.facade.get_all_places()), 2)

    def test_update_place_price(self):
        place = self._make_place()
        updated = self.facade.update_place(place.id, {'price': 200.0})
        self.assertEqual(updated.price, 200.0)

    def test_update_place_not_found(self):
        self.assertIsNone(self.facade.update_place('nonexistent', {'price': 1}))

    def test_update_place_invalid_price(self):
        place = self._make_place()
        with self.assertRaises(ValueError):
            self.facade.update_place(place.id, {'price': -10})

    def test_update_place_amenities(self):
        place = self._make_place(amenities=[self.amenity.id])
        self.assertEqual(len(place.amenities), 1)
        self.facade.update_place(place.id, {'amenities': []})
        self.assertEqual(len(place.amenities), 0)


class TestFacadeReview(unittest.TestCase):
    """Tests for review operations in HBnBFacade."""

    def setUp(self):
        self.facade = HBnBFacade()
        self.user = self.facade.create_user({
            'first_name': 'Reviewer', 'last_name': 'User',
            'email': 'rev@test.com', 'password': 'p'
        })
        self.place = self.facade.create_place({
            'title': 'Test Place', 'description': 'x',
            'price': 50.0, 'latitude': 0.0, 'longitude': 0.0,
            'owner_id': self.user.id
        })

    def _make_review(self, **kwargs):
        defaults = {
            'text': 'Great stay!',
            'rating': 5,
            'user_id': self.user.id,
            'place_id': self.place.id,
        }
        defaults.update(kwargs)
        return self.facade.create_review(defaults)

    def test_create_review_success(self):
        review = self._make_review()
        self.assertEqual(review.text, 'Great stay!')
        self.assertEqual(review.rating, 5)

    def test_create_review_links_to_place(self):
        review = self._make_review()
        self.assertIn(review, self.place.reviews)

    def test_create_review_invalid_user(self):
        with self.assertRaises(ValueError):
            self._make_review(user_id='nonexistent')

    def test_create_review_invalid_place(self):
        with self.assertRaises(ValueError):
            self._make_review(place_id='nonexistent')

    def test_create_review_empty_text(self):
        with self.assertRaises(ValueError):
            self._make_review(text='')

    def test_create_review_rating_too_high(self):
        with self.assertRaises(ValueError):
            self._make_review(rating=6)

    def test_create_review_rating_too_low(self):
        with self.assertRaises(ValueError):
            self._make_review(rating=0)

    def test_create_review_rating_not_int(self):
        with self.assertRaises(ValueError):
            self._make_review(rating=4.5)

    def test_get_review(self):
        review = self._make_review()
        found = self.facade.get_review(review.id)
        self.assertEqual(found.id, review.id)

    def test_get_review_not_found(self):
        self.assertIsNone(self.facade.get_review('nonexistent'))

    def test_get_all_reviews(self):
        self._make_review()
        self._make_review(text='Good', rating=4)
        self.assertEqual(len(self.facade.get_all_reviews()), 2)

    def test_get_reviews_by_place(self):
        self._make_review()
        self._make_review(text='Also good', rating=3)
        reviews = self.facade.get_reviews_by_place(self.place.id)
        self.assertEqual(len(reviews), 2)

    def test_update_review(self):
        review = self._make_review()
        updated = self.facade.update_review(
            review.id, {'text': 'Updated!', 'rating': 3})
        self.assertEqual(updated.text, 'Updated!')
        self.assertEqual(updated.rating, 3)

    def test_update_review_invalid_rating(self):
        review = self._make_review()
        with self.assertRaises(ValueError):
            self.facade.update_review(review.id, {'rating': 10})

    def test_update_review_not_found(self):
        self.assertIsNone(self.facade.update_review('nonexistent', {'text': 'x'}))

    def test_delete_review_success(self):
        review = self._make_review()
        result = self.facade.delete_review(review.id)
        self.assertTrue(result)
        self.assertIsNone(self.facade.get_review(review.id))

    def test_delete_review_removes_from_place(self):
        review = self._make_review()
        self.facade.delete_review(review.id)
        self.assertNotIn(review, self.place.reviews)

    def test_delete_review_not_found(self):
        self.assertFalse(self.facade.delete_review('nonexistent'))


if __name__ == '__main__':
    unittest.main()
