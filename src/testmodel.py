import os
from unittest import TestCase
os.environ.setdefault('DATABASE_URL', 'postgresql:///testdb')
from app import db, app, handle_message, User


##############################################################################
#For this cases each escenario will create the sample data that needs for the code that we're testing.

class FlaskTestsDatabase(TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Create tables and add sample data
        db.create_all()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_creates_a_new_user(self):
        """This test is for db, so it needs to show all the user in my db"""

        reply = handle_message(message="HI", sender_id="234567")

        self.assertEqual("Grettings, what is your name? ", reply)
        self.assertTrue(User.query.filter(User.facebook_id == "234567").one())

if __name__ == "__main__":
    import unittest

    unittest.main()