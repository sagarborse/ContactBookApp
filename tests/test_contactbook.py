import unittest
import os
import json
from app import create_app, db


class ContactBookTestCase(unittest.TestCase):
    """This class represents the contactbook test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.contactbook = {'name': 'Go to Borabora for vacation'}
        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            print("*****")
            db.session.close()
            db.drop_all()
            db.create_all()
            print("&&&&&")

    def register_user(self, email="user@test.com", password="test1234"):
        """This helper method helps register a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        """This helper method helps log in a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/login', data=user_data)

    def test_contactbook_creation(self):
        """Test API can create a contactbook (POST request)"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post('/contactbooks/', headers=dict(Authorization="Bearer " + access_token), data=self.contactbook)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Go to Borabora', str(res.data))

    def test_api_can_get_all_contactbooks(self):
        """Test API can get a contactbook (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post('/contactbooks/', 
                                 headers=dict(Authorization="Bearer " + access_token),
                                 data=self.contactbook)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/contactbooks/', headers=dict(Authorization="Bearer " + access_token),)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go to Borabora', str(res.data))

    def test_api_can_get_contactbook_by_id(self):
        """Test API can get a single contactbook by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post('/contactbooks/', headers=dict(Authorization="Bearer " + access_token), data=self.contactbook)
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/contactbooks/{}'.format(result_in_json['id']), headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Go to Borabora', str(result.data))

    def test_contactbook_can_be_edited(self):
        """Test API can edit an existing contactbook. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        
        rv = self.client().post(
            '/contactbooks/', headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Eat, pray and love'})
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            '/contactbooks/1', headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Dont just eat, but also pray and love :-)"
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client().get('/contactbooks/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Dont just eat', str(results.data))

    def test_contactbook_deletion(self):
        """Test API can delete an existing contactbook. (DELETE request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/contactbooks/', headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Eat, pray and love'})
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete('/contactbooks/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/contactbooks/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()