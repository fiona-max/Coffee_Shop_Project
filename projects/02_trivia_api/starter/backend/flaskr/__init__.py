import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = SQLAlchemy(app)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app)

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

    @app.route('/categories')
    def get_categories():
        categories = {category.id: category.type for category in Category.query.all()}
        return jsonify({'success': True,
                        'categories': categories
                        })

    '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        questions = Question.query.all()
        formatted_questions = [question.format() for question in questions]
        categories = {category.id: category.type for category in Category.query.all()}

        return jsonify({'success': True,
                        'questions': formatted_questions[start:end],
                        'total_number_of_questions': len(formatted_questions),
                        'categories': categories,
                        'currentCategory': 'NOT specified'
                        })

    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def question_delete(question_id):
        question = Question.query.get(question_id)
        db.session.delete(question)
        db.session.commit()

        return "question was successfully deleted"

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

    @cross_origin()
    @app.route('/questions', methods=['POST'])
    def add_question():
        question_data = request.json

        question = question_data['question']
        answer = question_data['answer']
        category = question_data['category']
        difficulty = question_data['difficulty']

        new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)

        db.session.add(new_question)
        db.session.commit()

        ques = Question.query.get(new_question.id)

        return jsonify({'success': True})

    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

    @cross_origin()
    @app.route('/questions', methods=['POST'])
    def search_question():
        my_questions = []
        search_term = request.form.get('search_term', '')
        results = Question.query.filter(Question.question.ilike(f"%{search_term}%"))
        my_questions.append(results)
        return jsonify({'success': True,
                        'questions': my_questions,
                        'totalQuestions': len(my_questions),
                        # 'currentCategory': 'Entertainment'
                        })

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        my_list = []
        questions = Question.query.filter(Question.id == id).one_or_none()
        print(questions)
        my_list.append(questions.format())
        # formatted_questions = [question.format() for question in questions]
        return jsonify({'success': True,
                        'categories': my_list,
                        'totalQuestions': len(my_list),
                        # 'currentCategory': questions
                        })

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

    # @cross_origin()
    # @app.route('/quizzes', methods=['POST'])
    # def add_quizz():

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

    return app
