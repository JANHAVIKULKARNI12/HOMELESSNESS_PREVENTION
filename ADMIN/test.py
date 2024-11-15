import unittest
from app import app, db, User, Admin
from werkzeug.security import check_password_hash

class UserRegistrationTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_registration(self):
        response = self.app.post('/register', data={
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        })
        user = User.query.filter_by(email='testuser@example.com').first()
        self.assertIsNotNone(user)
        self.assertTrue(check_password_hash(user.password, 'testpassword123'))
        self.assertFalse(user.is_verified)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/verify', response.location)

class AdminAdditionTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()
            superadmin = Admin(username='superadmin', password='superpassword', role='superadmin')
            db.session.add(superadmin)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_admin_adding(self):
        response = self.app.post('/admin/add', data={
            'username': 'newadmin',
            'password': 'newadminpassword',
            'role': 'admin'
        })
        new_admin = Admin.query.filter_by(username='newadmin').first()
        self.assertIsNotNone(new_admin)
        self.assertTrue(check_password_hash(new_admin.password, 'newadminpassword'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/dashboard', response.location)

if __name__ == '__main__':
    unittest.main()
