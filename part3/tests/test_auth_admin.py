"""
Tests for Task 4: JWT Authentication & Admin Authorization.
Run with: python3 -m unittest tests/test_auth_admin.py -v
"""
import json
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db
from config import DevelopmentConfig


class TestConfig(DevelopmentConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class TestAuthentication(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.h = {'Content-Type': 'application/json'}
        with self.app.app_context():
            db.create_all()
            # Register a regular user
            self.client.post('/api/v1/users/', headers=self.h,
                             data=json.dumps({
                                 'first_name': 'Test', 'last_name': 'User',
                                 'email': 'user@test.com', 'password': 'pass123'
                             }))

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def _login(self, email='user@test.com', password='pass123'):
        res = self.client.post('/api/v1/auth/login', headers=self.h,
                               data=json.dumps({'email': email,
                                                'password': password}))
        return json.loads(res.data).get('access_token'), res.status_code

    # ── Authentication tests ──────────────────────────────────────────────────

    def test_login_returns_token(self):
        token, status = self._login()
        self.assertEqual(status, 200)
        self.assertIsNotNone(token)

    def test_login_wrong_password_401(self):
        _, status = self._login(password='wrongpass')
        self.assertEqual(status, 401)

    def test_login_nonexistent_user_401(self):
        _, status = self._login(email='nobody@test.com')
        self.assertEqual(status, 401)

    def test_protected_endpoint_no_token_401(self):
        res = self.client.get('/api/v1/users/')
        self.assertEqual(res.status_code, 401)

    def test_protected_endpoint_with_token_200(self):
        token, _ = self._login()
        res = self.client.get('/api/v1/users/',
                              headers={**self.h, 'Authorization': f'Bearer {token}'})
        self.assertEqual(res.status_code, 200)

    # ── Authorization tests ───────────────────────────────────────────────────

    def test_regular_user_cannot_update_other_user(self):
        # Create second user
        r2 = self.client.post('/api/v1/users/', headers=self.h,
                              data=json.dumps({
                                  'first_name': 'Other', 'last_name': 'User',
                                  'email': 'other@test.com', 'password': 'pass'
                              }))
        other_id = json.loads(r2.data)['id']
        token, _ = self._login()
        res = self.client.put(f'/api/v1/users/{other_id}',
                              headers={**self.h, 'Authorization': f'Bearer {token}'},
                              data=json.dumps({'first_name': 'Hacked'}))
        self.assertEqual(res.status_code, 403)

    def test_regular_user_cannot_create_amenity(self):
        token, _ = self._login()
        res = self.client.post('/api/v1/amenities/',
                               headers={**self.h, 'Authorization': f'Bearer {token}'},
                               data=json.dumps({'name': 'Pool'}))
        self.assertEqual(res.status_code, 403)

    def test_regular_user_cannot_access_admin_endpoints(self):
        token, _ = self._login()
        res = self.client.post('/api/v1/admin/users',
                               headers={**self.h, 'Authorization': f'Bearer {token}'},
                               data=json.dumps({
                                   'first_name': 'X', 'last_name': 'Y',
                                   'email': 'x@y.com', 'password': 'p'
                               }))
        self.assertEqual(res.status_code, 403)

    def test_cannot_review_own_place(self):
        token, _ = self._login()
        auth_h = {**self.h, 'Authorization': f'Bearer {token}'}
        # Create place
        pr = self.client.post('/api/v1/places/', headers=auth_h,
                              data=json.dumps({
                                  'title': 'My Place', 'price': 100.0,
                                  'latitude': 0.0, 'longitude': 0.0
                              }))
        place_id = json.loads(pr.data)['id']
        # Try to review own place
        res = self.client.post('/api/v1/reviews/', headers=auth_h,
                               data=json.dumps({
                                   'text': 'Self review', 'rating': 5,
                                   'place_id': place_id
                               }))
        self.assertEqual(res.status_code, 400)


class TestAdminEndpoints(unittest.TestCase):
    """Task 4: Admin endpoint tests."""

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.h = {'Content-Type': 'application/json'}
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def _create_admin_and_login(self):
        """Directly insert an admin user and get a token."""
        from app.models.user import User
        from app import db as _db
        with self.app.app_context():
            admin = User(first_name='Admin', last_name='User',
                         email='admin@test.com', password='adminpass',
                         is_admin=True)
            _db.session.add(admin)
            _db.session.commit()
        res = self.client.post('/api/v1/auth/login', headers=self.h,
                               data=json.dumps({'email': 'admin@test.com',
                                                'password': 'adminpass'}))
        return json.loads(res.data)['access_token']

    def test_admin_can_create_user(self):
        token = self._create_admin_and_login()
        res = self.client.post('/api/v1/admin/users',
                               headers={**self.h, 'Authorization': f'Bearer {token}'},
                               data=json.dumps({
                                   'first_name': 'New', 'last_name': 'User',
                                   'email': 'new@test.com', 'password': 'pass'
                               }))
        self.assertEqual(res.status_code, 201)

    def test_admin_can_create_amenity(self):
        token = self._create_admin_and_login()
        res = self.client.post('/api/v1/admin/amenities',
                               headers={**self.h, 'Authorization': f'Bearer {token}'},
                               data=json.dumps({'name': 'Rooftop Pool'}))
        self.assertEqual(res.status_code, 201)

    def test_admin_can_update_any_user(self):
        # Create regular user first
        r = self.client.post('/api/v1/users/', headers=self.h,
                             data=json.dumps({
                                 'first_name': 'Regular', 'last_name': 'User',
                                 'email': 'regular@test.com', 'password': 'pass'
                             }))
        uid = json.loads(r.data)['id']
        token = self._create_admin_and_login()
        res = self.client.put(f'/api/v1/admin/users/{uid}',
                              headers={**self.h, 'Authorization': f'Bearer {token}'},
                              data=json.dumps({'first_name': 'Updated'}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data)['first_name'], 'Updated')

    def test_admin_can_delete_user(self):
        r = self.client.post('/api/v1/users/', headers=self.h,
                             data=json.dumps({
                                 'first_name': 'Del', 'last_name': 'User',
                                 'email': 'del@test.com', 'password': 'pass'
                             }))
        uid = json.loads(r.data)['id']
        token = self._create_admin_and_login()
        res = self.client.delete(f'/api/v1/admin/users/{uid}',
                                 headers={**self.h, 'Authorization': f'Bearer {token}'})
        self.assertEqual(res.status_code, 200)


if __name__ == '__main__':
    unittest.main()

