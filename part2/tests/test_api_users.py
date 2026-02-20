"""Tests for User API endpoints."""
import unittest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app


class TestUserEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.headers = {'Content-Type': 'application/json'}

    def _create_user(self, email='test@example.com'):
        return self.client.post('/api/v1/users/', headers=self.headers,
                                data=json.dumps({
                                    'first_name': 'John',
                                    'last_name': 'Doe',
                                    'email': email,
                                    'password': 'secret'
                                }))

    def test_create_user_201(self):
        res = self._create_user()
        self.assertEqual(res.status_code, 201)

    def test_create_user_returns_id(self):
        res = self._create_user()
        data = json.loads(res.data)
        self.assertIn('id', data)

    def test_create_user_no_password_in_response(self):
        res = self._create_user()
        data = json.loads(res.data)
        self.assertNotIn('password', data)

    def test_create_user_duplicate_email_400(self):
        self._create_user()
        res = self._create_user()
        self.assertEqual(res.status_code, 400)

    def test_create_user_invalid_email_400(self):
        res = self.client.post('/api/v1/users/', headers=self.headers,
                               data=json.dumps({
                                   'first_name': 'A', 'last_name': 'B',
                                   'email': 'bademail', 'password': 'x'
                               }))
        self.assertEqual(res.status_code, 400)

    def test_get_all_users_200(self):
        res = self.client.get('/api/v1/users/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json.loads(res.data), list)

    def test_get_user_by_id_200(self):
        create_res = self._create_user()
        user_id = json.loads(create_res.data)['id']
        res = self.client.get(f'/api/v1/users/{user_id}')
        self.assertEqual(res.status_code, 200)

    def test_get_user_not_found_404(self):
        res = self.client.get('/api/v1/users/nonexistent')
        self.assertEqual(res.status_code, 404)

    def test_update_user_200(self):
        create_res = self._create_user()
        user_id = json.loads(create_res.data)['id']
        res = self.client.put(f'/api/v1/users/{user_id}',
                              headers=self.headers,
                              data=json.dumps({'first_name': 'Updated'}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data)['first_name'], 'Updated')

    def test_update_user_not_found_404(self):
        res = self.client.put('/api/v1/users/nonexistent',
                              headers=self.headers,
                              data=json.dumps({'first_name': 'X'}))
        self.assertEqual(res.status_code, 404)


class TestAmenityEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.headers = {'Content-Type': 'application/json'}

    def _create_amenity(self, name='WiFi'):
        return self.client.post('/api/v1/amenities/', headers=self.headers,
                                data=json.dumps({'name': name}))

    def test_create_amenity_201(self):
        res = self._create_amenity()
        self.assertEqual(res.status_code, 201)

    def test_create_amenity_empty_name_400(self):
        res = self.client.post('/api/v1/amenities/', headers=self.headers,
                               data=json.dumps({'name': ''}))
        self.assertEqual(res.status_code, 400)

    def test_get_all_amenities_200(self):
        res = self.client.get('/api/v1/amenities/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json.loads(res.data), list)

    def test_get_amenity_by_id_200(self):
        create_res = self._create_amenity()
        aid = json.loads(create_res.data)['id']
        res = self.client.get(f'/api/v1/amenities/{aid}')
        self.assertEqual(res.status_code, 200)

    def test_get_amenity_not_found_404(self):
        res = self.client.get('/api/v1/amenities/nonexistent')
        self.assertEqual(res.status_code, 404)

    def test_update_amenity_200(self):
        create_res = self._create_amenity()
        aid = json.loads(create_res.data)['id']
        res = self.client.put(f'/api/v1/amenities/{aid}',
                              headers=self.headers,
                              data=json.dumps({'name': 'Fast WiFi'}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data)['name'], 'Fast WiFi')

    def test_update_amenity_not_found_404(self):
        res = self.client.put('/api/v1/amenities/nonexistent',
                              headers=self.headers,
                              data=json.dumps({'name': 'x'}))
        self.assertEqual(res.status_code, 404)


class TestPlaceEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.headers = {'Content-Type': 'application/json'}
        # Create a user and amenity for use in place tests
        user_res = self.client.post('/api/v1/users/', headers=self.headers,
                                    data=json.dumps({
                                        'first_name': 'Owner',
                                        'last_name': 'User',
                                        'email': 'owner@place.com',
                                        'password': 'p'
                                    }))
        self.owner_id = json.loads(user_res.data)['id']
        amenity_res = self.client.post('/api/v1/amenities/', headers=self.headers,
                                       data=json.dumps({'name': 'Pool'}))
        self.amenity_id = json.loads(amenity_res.data)['id']

    def _create_place(self, **kwargs):
        defaults = {
            'title': 'Beach House',
            'description': 'Lovely',
            'price': 120.0,
            'latitude': 36.7,
            'longitude': 3.0,
            'owner_id': self.owner_id,
        }
        defaults.update(kwargs)
        return self.client.post('/api/v1/places/', headers=self.headers,
                                data=json.dumps(defaults))

    def test_create_place_201(self):
        res = self._create_place()
        self.assertEqual(res.status_code, 201)

    def test_create_place_with_amenities(self):
        res = self._create_place(amenities=[self.amenity_id])
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(len(data['amenities']), 1)

    def test_create_place_response_has_owner(self):
        res = self._create_place()
        data = json.loads(res.data)
        self.assertIn('owner', data)
        self.assertIn('first_name', data['owner'])

    def test_create_place_invalid_owner_400(self):
        res = self._create_place(owner_id='nonexistent')
        self.assertEqual(res.status_code, 400)

    def test_create_place_negative_price_400(self):
        res = self._create_place(price=-1)
        self.assertEqual(res.status_code, 400)

    def test_create_place_invalid_latitude_400(self):
        res = self._create_place(latitude=200)
        self.assertEqual(res.status_code, 400)

    def test_create_place_invalid_longitude_400(self):
        res = self._create_place(longitude=200)
        self.assertEqual(res.status_code, 400)

    def test_get_all_places_200(self):
        res = self.client.get('/api/v1/places/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json.loads(res.data), list)

    def test_get_place_by_id_200(self):
        create_res = self._create_place()
        pid = json.loads(create_res.data)['id']
        res = self.client.get(f'/api/v1/places/{pid}')
        self.assertEqual(res.status_code, 200)

    def test_get_place_not_found_404(self):
        res = self.client.get('/api/v1/places/nonexistent')
        self.assertEqual(res.status_code, 404)

    def test_update_place_200(self):
        create_res = self._create_place()
        pid = json.loads(create_res.data)['id']
        res = self.client.put(f'/api/v1/places/{pid}',
                              headers=self.headers,
                              data=json.dumps({'price': 200.0}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data)['price'], 200.0)

    def test_get_place_reviews_200(self):
        create_res = self._create_place()
        pid = json.loads(create_res.data)['id']
        res = self.client.get(f'/api/v1/places/{pid}/reviews')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(json.loads(res.data), list)

    def test_get_reviews_place_not_found_404(self):
        res = self.client.get('/api/v1/places/nonexistent/reviews')
        self.assertEqual(res.status_code, 404)


class TestReviewEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.headers = {'Content-Type': 'application/json'}
        user_res = self.client.post('/api/v1/users/', headers=self.headers,
                                    data=json.dumps({
                                        'first_name': 'Rev',
                                        'last_name': 'User',
                                        'email': 'rev@review.com',
                                        'password': 'p'
                                    }))
        self.user_id = json.loads(user_res.data)['id']
        place_res = self.client.post('/api/v1/places/', headers=self.headers,
                                     data=json.dumps({
                                         'title': 'Test Place',
                                         'description': 'x',
                                         'price': 50.0,
                                         'latitude': 0.0,
                                         'longitude': 0.0,
                                         'owner_id': self.user_id
                                     }))
        self.place_id = json.loads(place_res.data)['id']

    def _create_review(self, **kwargs):
        defaults = {
            'text': 'Great!',
            'rating': 5,
            'user_id': self.user_id,
            'place_id': self.place_id,
        }
        defaults.update(kwargs)
        return self.client.post('/api/v1/reviews/', headers=self.headers,
                                data=json.dumps(defaults))

    def test_create_review_201(self):
        res = self._create_review()
        self.assertEqual(res.status_code, 201)

    def test_create_review_invalid_user_400(self):
        res = self._create_review(user_id='nonexistent')
        self.assertEqual(res.status_code, 400)

    def test_create_review_invalid_place_400(self):
        res = self._create_review(place_id='nonexistent')
        self.assertEqual(res.status_code, 400)

    def test_create_review_empty_text_400(self):
        res = self._create_review(text='')
        self.assertEqual(res.status_code, 400)

    def test_create_review_bad_rating_400(self):
        res = self._create_review(rating=6)
        self.assertEqual(res.status_code, 400)

    def test_get_all_reviews_200(self):
        res = self.client.get('/api/v1/reviews/')
        self.assertEqual(res.status_code, 200)

    def test_get_review_by_id_200(self):
        create_res = self._create_review()
        rid = json.loads(create_res.data)['id']
        res = self.client.get(f'/api/v1/reviews/{rid}')
        self.assertEqual(res.status_code, 200)

    def test_get_review_not_found_404(self):
        res = self.client.get('/api/v1/reviews/nonexistent')
        self.assertEqual(res.status_code, 404)

    def test_update_review_200(self):
        create_res = self._create_review()
        rid = json.loads(create_res.data)['id']
        res = self.client.put(f'/api/v1/reviews/{rid}',
                              headers=self.headers,
                              data=json.dumps({'text': 'Updated!', 'rating': 3}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data)['text'], 'Updated!')

    def test_update_review_not_found_404(self):
        res = self.client.put('/api/v1/reviews/nonexistent',
                              headers=self.headers,
                              data=json.dumps({'text': 'x'}))
        self.assertEqual(res.status_code, 404)

    def test_delete_review_200(self):
        create_res = self._create_review()
        rid = json.loads(create_res.data)['id']
        res = self.client.delete(f'/api/v1/reviews/{rid}')
        self.assertEqual(res.status_code, 200)

    def test_delete_review_not_found_404(self):
        res = self.client.delete('/api/v1/reviews/nonexistent')
        self.assertEqual(res.status_code, 404)

    def test_delete_review_gone_after_delete(self):
        create_res = self._create_review()
        rid = json.loads(create_res.data)['id']
        self.client.delete(f'/api/v1/reviews/{rid}')
        res = self.client.get(f'/api/v1/reviews/{rid}')
        self.assertEqual(res.status_code, 404)


if __name__ == '__main__':
    unittest.main()
