from unittest import TestCase
from app import db
from flask_sqlalchemy import SQLAlchemy


##############################################################################
#For this cases each escenario will create the sample data that needs for the code that we're testing.

class FlaskTestsDatabase(TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Connect to test database
        db = SQLAlchemy(app, db_url="postgresql:///testdb")

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Create tables and add sample data
        db.create_all()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_it_returns_all_the_users(self):
        """This test is for db, so it needs to show all the user in my db"""
        pass

if __name__ == "__main__":
    import unittest

    unittest.main()