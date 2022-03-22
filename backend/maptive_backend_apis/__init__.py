import os
import random
import json
from flask import Flask, jsonify, make_response, request


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
        users_list = ''
        for user in query_db('select * from users'):
            print(user['username'], 'has the id', user['id'])
            users_list = users_list+str(user['username'])+'\n'

        return users_list

    # register new users
    @app.route('/registerUser', methods=['POST'])
    def registerUser():
        req_username = request.form.get('username')
        user = query_db('select * from users where username = ?',
                        [req_username], one=True)
        if user is None:
            print('No such user')
            insert_into_db('insert into users(username, questionnaire_filled) values (?,?)',
                           (req_username, 'False'))
            return 'New user added'

        else:
            print(req_username, 'has the id', user['id'])
        return 'User already exists'

    # get existing user
    @app.route('/fetchUser', methods=['POST'])
    def fetchUser():
        req_username = request.form.get('username')
        user = query_db('select * from users where username = ?',
                        [req_username], one=True)
        if user is None:
            print('No such user')
            return 'User does not exist'
        else:
            print(req_username, 'has the id', user['id'])
        return {'username': user['username'], 'questionnaire_filled': user['questionnaire_filled']}

    # get json question data
    @app.route('/question_data', methods=['GET'])
    def question_data():
        f = open('data_handling/data.json')
        data = json.load(f)
        response = jsonify({'data': data})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

   # get json question choice
    @app.route('/pick_question', methods=['GET'])
    def pick_question():
        f = open('data_handling/data.json')
        data = json.load(f)
        new_index = random.randint(0, len(data))
        response = jsonify({'index': new_index})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    # below api not needed? review

    # # Assuming front-end will send the username again, we can't have dups for now
    # @app.route('/questionnaire_done', methods=['POST'])
    # def questionnaire_done():
    #     form_username = request.form.get('username')

    #     # function to add to JSON
    #     with open('./user_data.json', 'r') as file:
    #         user_json_db = json.load(file)

    #     for user in user_json_db:
    #         if user['user_name'] == form_username:
    #             # Update the entry within the username of questionaire yesx
    #             user['questionnaire_filled'] = True
    #         print(user_json_db)
    #         print(type(user_json_db))

    #         with open('./user_data.json', 'w') as file:
    #             file.seek(0)
    #             json.dump(user_json_db, file, indent=4)

    #         # # Sets file's current position at offset.
    #         # file.seek(0)
    #         # # convert back to json.
    #         # json.dump(file_data, file, indent=4)
    #     return 'Questionnaire Done'

    def query_db(query, args=(), one=False):
        conn = db.get_db()
        cur = conn.execute(query, args)
        rv = cur.fetchall()
        conn.commit()
        cur.close()
        return (rv[0] if rv else None) if one else rv

    def insert_into_db(query, args=()):
        conn = db.get_db()
        cur = conn.execute(query, args)
        conn.commit()
        cur.close()

    from . import db
    db.init_app(app)

    return app
