import os
import random
import json
import sqlite3
import flask
from flask import abort
from flask import Flask, jsonify, make_response, request
from collections import defaultdict

# global variables
grades = ["1", "2", "3", "4", "5", "6", "7", "8", "G", "S", "A1", "A2"]
grade_to_difficulty_mapping = {
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "G": "9",
    "S": "10",
    "A1": "11",
    "A2": "12"
}
difficulty_to_grade_mapping = {
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "G",
    "10": "S",
    "11": "A1",
    "12": "A2"
}
gradeMappings = {
    "Geometry": "G",
    "Statistics": "S",
    "Algebra 1": "A1",
    "Algebra 2": "A2"
}

# flask app initialization


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # get all users in DB

    @app.route('/getAllUsers', methods=['GET'])
    def getAllUsers():
        users_dict = defaultdict(list)
        for user in query_db('select * from users'):
            users_dict[user['id']].append(user)
            print(users_dict)
        return users_dict

    # register new users
    # get grade and username from UI - this method will be called when user enters username+grade and clicks submit
    # OR when user completes questionnaire, grade is calculated, sent to UI and then username+grade is returned by UI
    # no need to store questionnaire_filled flag in this case
    # grade calculation via questionnaire is done in another method

    @app.route('/registerUser', methods=['POST'])
    def registerUser():
        user_info = request.get_json(force=True)
        req_username = user_info['username']
        req_difficulty_level = grade_to_difficulty_mapping.get(
            str(user_info['grade']))

        # below fields not needed as of now
        # categories = user_info['categories']
        # categories_string = ','.join(categories)

        user = query_db('select * from users where username = ?',
                        [req_username],
                        one=True)
        response = flask.Response()

        if user is None:
            print('No such user')
            try:
                insert_into_db(
                    'insert into users(username, difficulty_level, total_correct, total_incorrect) values (?,?,?,?)',
                    (req_username, req_difficulty_level, 0, 0))
                response = jsonify('New user added')

            except sqlite3.IntegrityError as e:
                print('Error Occured: ', e)
                abort(400)

        else:
            response = jsonify(req_username, 'has the id', user['id'])
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # get existing user

    @app.route('/fetchUser', methods=['POST'])
    def fetchUser():
        user_info = request.get_json()
        req_username = user_info['username']
        user = query_db('select * from users where username = ?',
                        [req_username],
                        one=True)
        if user is None:
            print('No such user')
            return 'User does not exist'
        else:
            print(req_username, 'has the id', user['id'])
        return user

    # get json question data

    @app.route('/getQuestionData', methods=['GET'])
    def question_data():
        f = open('data_handling/data.json')
        data = json.load(f)
        response = jsonify({'data': data})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # get json categories
    @app.route('/getCategories', methods=['POST'])
    def get_grade_categories():
        user_info = request.get_json(force=True)
        req_grade = user_info['grade']
        grade = req_grade
        if req_grade.isnumeric() == False:
            grade = gradeMappings[req_grade]
        grade_cats = set()
        f = open('data_handling/data.json')
        data = json.load(f)
        for item in data:
            if item["grade"] == grade:
                grade_cats.add(item["category"])
        grade_cats = list(grade_cats)
        response = jsonify({'categories': list(grade_cats)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # get json questionnaire questions for new user

    @app.route('/pickQuestionnaireQuestions', methods=['GET'])
    def pick_questionnaire_questions():
        f = open('data_handling/data.json')
        data = json.load(f)
        questions = []
        for grade in grades:
            question = next(x for x in data if x["grade"] == grade)
            questions.append(question)
        response = jsonify({'data': questions})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # method to store user responses in db

    def store_submissions(question_id, correct, username):
        try:
            # update correct answers into attempted_questions table
            if correct:
                insert_into_db(
                    'insert into attempted_questions(username, question_id, answered_correctly) values (?,?,?)',
                    (username, question_id, correct))

            # update total_correct and total_incorrect answers in users table
            user = query_db('select * from users where username = ?',
                            [username],
                            one=True)
            total_correct = int(user['total_correct']) + \
                (1 if correct else 0)
            total_incorrect = int(user['total_incorrect']) + \
                (1 if not correct else 0)
            print("Total Correct:", total_correct,
                  "Total Incorrect:", total_incorrect)
            update_db('update users set total_correct=?,total_incorrect=? where username = ?',
                      (total_correct, total_incorrect, username))
            print(query_db('select * from users'))  # debug

        except sqlite3.IntegrityError as e:
            print('Error Occured: ', e)
            pass

    # get json question choice
    @app.route('/pickQuestion', methods=['POST'])
    def pick_question():
        question_info = request.get_json(force=True)
        question = question_info['question']
        correct = question_info['correct']
        username = question_info['username']

        try:
            store_submissions(question, correct, username)
        except Exception as e:
            print(f'Exception Occured {e}')
            pass

        # get all correct questions attempted by user
        attempted_question_ids = query_db('select question_id from attempted_questions where username = ?',
                                          [username])

        attempted_questions_list = [int(item['question_id'])
                                    for item in attempted_question_ids]

        user_data = query_db(
            'select * from users where username = ?', [username], one=True)

        # get user difficulty level
        user_difficulty_level = int(user_data['difficulty_level'])
        print(user_difficulty_level)

        # get all question data
        f = open('data_handling/data.json')
        data = json.load(f)

        # get all question ids of current difficulty level of user except the ones already attempted
        valid_question_ids = []
        for index, item in enumerate(data):
            if (item['difficulty'] == user_difficulty_level) and (get_question_id(item['skillno']) not in attempted_questions_list):
                valid_question_ids.append(index)
        if valid_question_ids:
            next_index = random.choice(valid_question_ids)
        else:
            next_index = random.choice(valid_question_ids)
        # grade checking logic
        total_attempted = user_data['total_correct'] + \
            user_data['total_incorrect']
        # do this for every 10th question attempted or when no more valid questions left in current grade
        grade_change = "NONE"
        if total_attempted != 0 and total_attempted % 10 == 0 or not valid_question_ids:        # avoid division by 0
            grade_change = grade_reccomendation(
                user_data['total_correct'], total_attempted)
            update_user_grade(username, grade_change)

        response = jsonify({'index': next_index, 'grade_update': grade_change})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # get question id from skillno string

    def get_question_id(skill_no_str):
        keyword = 'skillno='
        _, _, after_keyword = skill_no_str.partition(keyword)
        return int(after_keyword)

    # grade reccomendation logic

    def grade_reccomendation(total_correct, total_attempted):
        # This would recommend a newer or same grade depending on the win/loss rate.
        # If the user agrees to the next grade then the front end can request a question for grade+1 and category
        # we would also update the current grade and category of the user in the users table
        win_rate = total_correct / total_attempted

        if win_rate > 0.8:
            return 'UPGRADE'

        elif win_rate < 0.25:
            return 'DOWNGRADE'

        else:
            return 'NONE'

    # grade update based on user response
    # @app.route('/updateUserGrade', methods=['POST'])
    def update_user_grade(username, grade_change):
        # req_data = request.get_json()
        # username = req_data['username']
        user = query_db('select * from users where username=?',
                        [username], one=True)

        difficulty_level = user['difficulty_level']
        total_correct = user['total_correct']
        total_incorrect = user['total_incorrect']

        if grade_change == 'UPGRADE':
            difficulty_level += 1
            total_correct = 0
            total_incorrect = 0
        elif grade_change == 'DOWNGRADE':
            difficulty_level -= 1
            total_correct = 0
            total_incorrect = 0

        # else no change for no grade update by user
        if grade_change != 'NONE':
            update_db('update users set difficulty_level=?,total_correct=?,total_incorrect=? where username = ?',
                      (difficulty_level, total_correct, total_incorrect, username))
        return 'Update Successful'

    # get attempted questiond for a user
    # for debugging

    @ app.route('/getAttemptedQuestions', methods=['POST'])
    def attempted_questions():
        req = request.get_json()
        username = req['username']
        user_attempted_questions = query_db(
            'select * from attempted_questions where username=?', [username])
        print(user_attempted_questions)
        if user_attempted_questions is None:
            return 'No questions attempted'

        response = jsonify(user_attempted_questions)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def query_db(query, args=(), one=False):
        conn = db.get_db()
        conn.row_factory = dict_factory
        cur = conn.execute(query, args)
        rv = cur.fetchall()
        conn.commit()
        cur.close()
        return (rv[0] if rv else None) if one else rv

    def insert_into_db(query, args=()):
        conn = db.get_db()
        conn.row_factory = dict_factory
        cur = conn.execute(query, args)
        conn.commit()
        cur.close()

    def update_db(query, args=()):
        conn = db.get_db()
        cur = conn.execute(query, args)
        conn.commit()
        cur.close()

    from . import db
    db.init_app(app)

    return app
