import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_password = '123456'
        self.database_user = 'GG-2'
        self.database_host = '127.0.0.1:5432'
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.database_user, self.database_password,
                                                               self.database_host, self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': "What is a lake?",
            'answer': "An omnivore",
            'category': "4",
            'difficulty': "4"
        }
        self.new_search_term = {
            'searchTerm': "penicillin"
        }
        self.search_term = {
            'searchTerm': "qendorilia"
        }
        self.new_quizzes = {
            'previous_questions': [13, 14],
            'quiz_category': "3",
        }
        self.quiz_test = {
            'previous_questions': [13, 14],
            'quiz_category': {
                'id': 3
            },
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))

    def test_retrieve_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_delete_question(self):
        res = self.client().delete('/questions/12')
        data = json.loads(res.data)

        a_question = Question.query.filter(Question.id == 12).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 12)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(a_question, None)

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete('/questions/78')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_add_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))

    def test_405_if_book_creation_not_allowed(self):
        res = self.client().post('/questions/46', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "method not allowed")

    def test_retrieve_questions_based_on_category(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_retrieve_question_not_found(self):
        res = self.client().get('/categories/6/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_search_questions(self):
        res = self.client().post('/questions', json=self.new_search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_search_questions_not_found(self):
        res = self.client().post('/questions', json=self.search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_play_quiz(self):
        res = self.client().post('/quizzes', json=self.quiz_test)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue((data['question']))

    def test_405_if_quizz_creation_not_allowed(self):
        res = self.client().post('/quizzes', json=self.new_quizzes)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "method not allowed")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
