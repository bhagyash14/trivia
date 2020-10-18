import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

NUM_OF_QUESTIONS_PER_PAGE = 10

  # create and configure the app
  def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={'/': {'origins': '*'}})

    @app.after_request
    def after_request(response):
      response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
      return response

  #Create an endpoint to handle GET requests for all available categories.
  @app.route('/categories')
  def get_categories():
      try:
        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
          categories_dict[category.id] = category.type
        return jsonify({
            'success': True,
            'categories': categories_dict
        }),200
      except Exception:
          abort(404)

  #Create an endpoint to handle GET requests for questions 
  @app.route('/questions')
  def get_questions():
      try:
        questions_data = Question.query.all()
        categories = Category.query.all()

        questions_count = len(questions_data)
        this_page_questions = get_paginated_data(request, questions_data)
              
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type
        
        return jsonify({
            'success': True,
            'categories': categories_dict,
            'questions_count': questions_count,
            'questions': this_page_questions
        }),200
      except Exception:
          abort(404)

  #Create an endpoint to DELETE question using a question ID. 
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
        try:
            question = Question.query.filter_by(id=id).one_or_none()
            if question is None:
                abort(404)

            question.delete()
            return jsonify({
                'success': True,
                'message': "Question has been deleted"
                'deleted': id
            }),200

        except:
            abort(422)

  #Create an endpoint to POST a new question.
  @app.route('/questions', methods=['POST'])
  def post_question():
        input_data = request.get_json()

        new_question = input_data.get('question')
        new_answer = input_data.get('answer')
        new_difficulty = input_data.get('difficulty')
        new_category = input_data.get('category')

        if ((new_question == '') or (new_answer == '')
                or (new_difficulty == '') or (new_category == '')):
            abort(422)
        
        try:
            question = Question(question=new_question, 
                                answer=new_answer,
                                difficulty=new_difficulty, 
                                category=new_category)
            question.insert()

            return jsonify({
                'success': True,
                'message': 'Question has been posted successfully!!'
            }), 201
        except:
            abort(422)

  #Get questions based on a search term
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
        input_data = request.get_json()
        search_term = input_data.get('searchTerm')
        
        if (input_data.get('searchTerm')):
            
            result_set = Question.query.
                filter(Question.question.ilike(f'%{search_term}%')).all()

            if (len(result_set) == 0):
                abort(404)

            paginated_result = get_paginated_data(request, result_set)
            return jsonify({
                'success': True,
                'questions': paginated_result,
            }),200

  #Create a GET endpoint to get questions based on category. 
  
  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
        category = Category.query.filter_by(id=id).one_or_none()
        if (category is None):
            abort(400)

        result_set = Question.query.filter_by(category=category.id).all()
        paginated_output = get_paginated_data(request, result_set)

        return jsonify({
            'success': True,
            'current_category': category.type
            'questions': paginated_output            
        })

  #Create a POST endpoint to get questions to play the quiz.
  
  @app.route('/quizzes', methods=['POST'])
  def get_random_quiz_question():
        input_data = request.get_json()
        previous_questions = input_data.get('previous_questions')
        quiz_category = input_data.get('quiz_category')

        if ((previous_questions is None) or (quiz_category is None)):
            abort(400)

        if (quiz_category['id'] == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=quiz_category['id']).all()

        total = len(questions)

        def get_random_question():
            return questions[random.randrange(0, len(questions), 1)]

        def check_if_previously_used(question):
            used_peviously_flag = False
            for q in previous_questions:
                if (q == question.id):
                    used_peviously_flag = True

            return used_peviously_flag

        question = get_random_question()

        while (check_if_previously_used(question)):
            question = get_random_question()

        return jsonify({
            'success': True,
            'question': question.format()
        }),200
  
  #Create error handlers for all expected errors including 404 and 422. 
  @app.errorhandler(400)
  def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400


  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422

  #Utility to get paginated output
  def get_paginated_data(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * NUM_OF_QUESTIONS_PER_PAGE
    end = start + NUM_OF_QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

  return app

