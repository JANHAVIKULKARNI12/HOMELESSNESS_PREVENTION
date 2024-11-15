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

class TestDatabaseInitialization(unittest.TestCase):
    
    def setUp(self):
        # Set up the test environment
        self.app = app.test_client()
        self.app.testing = True

        # Create an app context and initialize the database
        with app.app_context():
            db.create_all()  # Creates tables
            # Add sample people records if not already added
            if not Person.query.first():
                sample_people = [
                    Person(name="John Doe", age=35, gender="Male", income_level=15000.00, homeless_status=False),
                    Person(name="Jane Smith", age=28, gender="Female", income_level=12000.00, homeless_status=False),
                    Person(name="Mike Johnson", age=40, gender="Male", income_level=10000.00, homeless_status=True),
                    Person(name="Emily Davis", age=30, gender="Female", income_level=20000.00, homeless_status=False),
                    Person(name="Chris Lee", age=45, gender="Male", income_level=8000.00, homeless_status=True)
                ]
                db.session.bulk_save_objects(sample_people)
                db.session.commit()

    def tearDown(self):
        # Clean up the database after each test
        with app.app_context():
            db.drop_all()

    def test_sample_people_added(self):
        # Query the database for the sample people records
        with app.app_context():
            people = Person.query.all()
            self.assertEqual(len(people), 5)  # There should be 5 records in the database
            self.assertEqual(people[0].name, "John Doe")
            self.assertEqual(people[1].name, "Jane Smith")
            self.assertEqual(people[2].name, "Mike Johnson")
            self.assertEqual(people[3].name, "Emily Davis")
            self.assertEqual(people[4].name, "Chris Lee")
    
    def test_database_initialized(self):
        # Verify that the database has been initialized with sample data
        with app.app_context():
            people = Person.query.all()
            self.assertGreater(len(people), 0, "No sample data found in the database.")
            for person in people:
                self.assertIsInstance(person.name, str)
                self.assertIsInstance(person.age, int)

if __name__ == '__main__':
    unittest.main()
