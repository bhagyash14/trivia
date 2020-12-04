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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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
    def test_get_all_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_invalid_category_id(self):
        response = self.client().get('/categories/18543/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_get_all_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])


    def test_invalid_page_request(self):
        response = self.client().get('/questions?page=999')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_success_delete_question(self):
        question = Question(question=self.new_question['question'], 
                            answer=self.new_question['answer'],
                            category=self.new_question['category'], 
                            difficulty=self.new_question['difficulty'])
        question.insert()
        qid = question.id
        questions_before_delete = Question.query.all()

        response = self.client().delete('/questions/{}'.format(qid))
        data = json.loads(response.data)
        questions_after_delete = Question.query.all()

        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], qid)
        self.assertTrue(len(questions_before_delete) - len(questions_after_delete) == 1)
        self.assertEqual(question, None)

    def test_invalid_delete_question_request(self):
        # this tests delete with invalid id
        response = self.client().delete('/questions/oju567')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_success_create_new_question(self):
        questions_before_post = Question.query.all()

        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        questions_after_post = Question.query.all()
        question = Question.query.filter_by(id=data['created']).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(questions_after_post) - len(questions_before_post) == 1)
        self.assertIsNotNone(question)

    def test_invalid_create_question(self):
        request = {
            'question': '',
            'answer': '',
            'difficulty': 2,
            'category': 1,
        }
        response = self.client().post('/questions', json=request)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_search_for_question(self):
        request_data = {
            'searchTerm': 'Donald Trump',
        }
        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_invalid_search_response(self):
        request_data = {
            'searchTerm': '',
        }
        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    

    


    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
