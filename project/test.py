# project/test.py


import os
import unittest

from views import app, db
from _config import basedir
from models import User

TEST_DB = 'test.db'




class AllTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    #################################
    ######## helper methods  ########
    #################################

    # login helper method
    def login(self, name, password):
        return self.app.post('/', data=dict(name=name, password=password), follow_redirects=True)

    # register helper method
    def register(self, name, email, password, confirm):
        return self.app.post(
            'register/',
            data=dict(name=name, email=email, password=password, confirm=confirm),
            follow_redirects=True
        )


    ###################################
    ############# test  ###############
    ###################################
    # each test should start with 'test'
    def test_user_setup(self):
        new_user = User("david", "david@meltwater.org", "davidopoku")
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            t.name
        assert t.name == "david"


    # form is present on login page
    def test_form_is_present_on_login(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please sign in to access your task list', response.data)


    # unregistered users cannot login
    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'bar')
        self.assertIn(b'Invalid username or password.', response.data)


    # registered users can login (form validation)
    def test_users_can_login(self):
        self.register('David', 'david@adoore.org', 'python', 'python')
        response = self.login('David', 'python')
        self.assertIn('Welcome to FlaskTaskr', response.data)


    # show error for invalid form data
    def test_invalid_form_data(self):
        self.register('David', 'david@meltwater.org', 'python', 'python')
        response = self.login('alert("alert box!");', 'foo')
        self.assertIn(b'Invalid username or password.', response.data)


    # form is present on register page
    def test_form_is_present_on_register_page(self):
        response = self.app.get('register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please register to access the task list.', response.data)


    # users can register (form validation)
    def test_user_registration_error(self):
        self.app.get('register/', follow_redirects=True)
        self.register('DavidOpoku', 'david@meltwater.org', 'python', 'python')
        self.app.get('register/', follow_redirects=True)
        response = self.register(
            'DavidOpoku', 'david@meltwater.org', 'python', 'python')
        self.assertIn(b'That username and/or email already exist.', response.data)

if __name__ == "__main__":
    unittest.main()