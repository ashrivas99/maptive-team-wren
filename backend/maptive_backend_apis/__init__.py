import os
import json

from flask import Flask, request


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
        # a simple page that says hello

    @app.route('/add_user', methods=['POST'])
    def add_user():
        # By default questionaire is No
        # Add username to json
        form_username = request.form.get('username')

        # function to add to JSON
        with open('./user_data.json', 'r+') as file:
            file_data = json.load(file)

            # new_data = {'user_name': {form_username}, 'questionnaire_filled': False}
            # file_data["users"].update(new_data)
            file_data.append({"user_name": form_username,
                              "questionnaire_filled": False})
            # # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent=4)

        return 'User added'

    @app.route('/fetch_user', methods=['GET'])
    def fetch_user():
        form_username = request.form.get('username')

        # Read user data
        with open('./user_data.json', 'r') as f:
            user_json_db = json.load(f)

        # Search in dict/json for the username
        for user in user_json_db:
            if user['user_name'] == form_username:
                return user

        return 'User Not Found'

    # Assuming front-end will send the username again, we can't have dups for now
    @app.route('/questionnaire_done', methods=['POST'])
    def questionnaire_done():
        form_username = request.form.get('username')

        # function to add to JSON
        with open('./user_data.json', 'r') as file:
            user_json_db = json.load(file)

        for user in user_json_db:
            if user['user_name'] == form_username:
                # Update the entry within the username of questionaire yesx
                user['questionnaire_filled'] = True
            print(user_json_db)
            print(type(user_json_db))

            with open('./user_data.json', 'w') as file:
                file.seek(0)
                json.dump(user_json_db, file, indent=4)

            # # Sets file's current position at offset.
            # file.seek(0)
            # # convert back to json.
            # json.dump(file_data, file, indent=4)
        return 'Questionnaire Done'

    return app
