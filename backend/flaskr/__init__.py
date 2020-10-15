import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/': {'origins': '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
      return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests for all available categories.
  '''
  @app.route('/categories')
  def get_categories():

        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
          categories_dict[category.id] = category.type

        if (len(categories_dict) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories_dict
        })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions 
  '''
  @app.route('/questions')
  def get_questions():
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)
              
        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type
        
        if (len(current_questions) == 0):
            abort(404)
        
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories_dict
        })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
        try:
            question = Question.query.filter_by(id=id).one_or_none()
            if question is None:
                abort(404)

            question.delete()
            return jsonify({
                'success': True,
                'deleted': id
            })

        except:
            abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question.
  '''
  @app.route('/questions', methods=['POST'])
  def post_question():
        body = request.get_json()
        if (body.get('searchTerm')):
            search_term = body.get('searchTerm')
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            if (len(selection) == 0):
                abort(404)
            paginated = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'questions': paginated,
                'total_questions': len(Question.query.all())
            })
        # if no search term, create new question
        else:
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_difficulty = body.get('difficulty')
            new_category = body.get('category')

            if ((new_question is None) or (new_answer is None)
                    or (new_difficulty is None) or (new_category is None)):
                abort(422)

            try:
                question = Question(question=new_question, answer=new_answer,
                                    difficulty=new_difficulty, category=new_category)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'question_created': question.question,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

            except:
                abort(422)


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
        category = Category.query.filter_by(id=id).one_or_none()
        if (category is None):
            abort(400)

        selection = Question.query.filter_by(category=category.id).all()
        paginated = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': paginated,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
        })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz.
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_random_quiz_question():
        body = request.get_json()
        previous = body.get('previous_questions')
        category = body.get('quiz_category')
        if ((category is None) or (previous is None)):
            abort(400)

        if (category['id'] == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=category['id']).all()

        total = len(questions)

        def get_random_question():
            return questions[random.randrange(0, len(questions), 1)]

        def check_if_used(question):
            used = False
            for q in previous:
                if (q == question.id):
                    used = True

            return used

        question = get_random_question()

        while (check_if_used(question)):
            question = get_random_question()

            if (len(previous) == total):
                return jsonify({
                    'success': True
                })

        return jsonify({
            'success': True,
            'question': question.format()
        })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

  @app.errorhandler(400)
  def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

  
  return app

    