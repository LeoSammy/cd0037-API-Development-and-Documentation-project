import os
from select import select
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import collections
collections.Iterable = collections.abc.Iterable

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    #CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization,true")
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=['GET'])
    def show_categories():
        categories_avail = Category.query.order_by(Category.id).all()
        category_list = {}
        for category in categories_avail:
            category_list[category.id] = category.type

        return jsonify(
            {
                "success": True,
                "categories": category_list,
                "total_categories": len(categories_avail),
            }
        )



    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions", methods=['GET'])
    def retrieve_questions():
        questions_selection = Question.query.order_by(Question.id).all()
        total_questions = len(questions_selection)
        questions_list = paginate_questions(request,questions_selection)

        if len(questions_selection) == 0:
            abort(404)
        

        category_list = Category.query.all()
        categories_avail = {}
        for category in category_list:
            categories_avail[category.id] = category.type

            for question in questions_selection:
                curr_category = question.category
        

        return jsonify(
            {
              "success": True,
              "questions": questions_list,
              "current_category": curr_category,
              "total_questions": total_questions,
              "categories": categories_avail,
            }
        )
    

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            total_questions = len(Question.query.all())


            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    "total_questions": total_questions,
                    "message": 'Question deleted'
                }
            )

        except:
            abort(422)    



    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=['POST'])
    def create_question():
        body  = request.get_json()

        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty= body.get('difficulty')
        
        search_term = body.get('searchTerm')

       

            #check if search_term is already present in database
        if search_term:

            selection = Question.query.order_by(Question.id).filter(Question.question.ilike("%{}%".format(search_term)))

            if (len(selection) == 0):
                    abort(404)
                
               
        else:    

            try:
                question = Question(question=new_question, answer=new_answer,category=new_category,difficulty=new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_question = paginate_questions(request, selection)
                total_quesitons = len(Question.query.all())
                return jsonify(
                        {
                            "success": True,
                            "created": question.id,
                            "question_added": question.question,
                            "questions": current_question,
                            "total_questions": total_quesitons,
                        }
                        )
                    
            except:
                    abort(422)
                
        
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/search", methods=['POST'])
    def find_questions():
        body = request.get_json()
        
        search_term = body.get("searchTerm")
        selection = Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()
        total_questions = len(selection)

        if (len(selection)== 0 ) or selection is None:
            return jsonify({
                "success": True,
                "questions": "Empty",
                "error": 404,
                "total_questions": total_questions
            })

        if selection:
            current_question_list = paginate_questions(request, selection)
            
            return jsonify({
                "success": True,
                "questions": current_question_list,
                "total_questions": total_questions
            })
        else: 
            abort(404)


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions", methods=['GET'])
    def category_question_list(category_id):

        category = Category.query.filter_by(id=category_id).one_or_none()
        selection = Question.query.filter_by(category = category_id).all()
        current_question_list = paginate_questions(request,selection)
        total_questions = len(selection)


        return jsonify({
            "success": True,
            "questions": current_question_list,
            "current_category": category.type,
            "total_questions": total_questions,
        })


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=['POST'])
    def get_quizzes():

        #load the given request body
        body = request.get_json()
         #get category of question
        quiz_category = body.get("quiz_category")
        #get the previous question from request
        previous_questions = body.get("previous_questions")
       

        if (quiz_category == None) or (previous_questions == None):
            abort(404)

        try:
            if (quiz_category['id'] == 0):
                question_list = Question.query.all()
                formated_questions = [question.format() for question in question_list]

            else:
                question_list=Question.query.filter_by(category=quiz_category['id']).all()
                formated_questions = [question.format() for question in question_list]
            
            #total questions listed
            total_questions = len(question_list)
            print("Formatted questions",formated_questions)
        
            #get a randon question
            random_question = random.randrange(0,total_questions,1)

            for question in formated_questions:
                if question['id'] in previous_questions:
                   return jsonify({
                    "message":"Question already checked"
                   })
                    
                else:
                    checked_question_list = formated_questions[random_question]
                    print("Checked question list", checked_question_list)


            if (len(previous_questions) == total_questions):
                return jsonify({"success":True
                                            })

            return jsonify({
            "success":True,
            "question":checked_question_list
                    })
        except:
            abort(404)
            
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': '404',
            'message': 'Resource Not Found'
        }), 404

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': '405',
            'message': 'Method Not Allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': '422',
            'message': 'Unprocessable'
        }), 422


    return app

