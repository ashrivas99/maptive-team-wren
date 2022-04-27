import os
import random
import json
import sqlite3
import flask
from flask import abort
from flask import Flask, jsonify, make_response, request
from collections import defaultdict
from pprint import pprint
import ast
import copy

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
    "A2": "12",
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
    "12": "A2",
}
gradeMappings = {
    "Geometry": "G",
    "Statistics": "S",
    "Algebra 1": "A1",
    "Algebra 2": "A2",
}

# flask app initialization


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # get all users in DB

    def get_categories(difficulty):
        difficulty_str = str(difficulty)
        grades = []
        if difficulty_str == "9":
            grades = ["G", "A1"]
        elif difficulty_str == "10":
            grades = ["S", "A2"]
        else:
            grades = [difficulty_str]

        grade_cats = set()
        f = open("data_handling/data.json")
        data = json.load(f)
        for item in data:
            if item["grade"] in grades:
                grade_cats.add(item["category"])
        grade_cats = list(grade_cats)
        return grade_cats

    @app.route("/getAllUsers", methods=["GET"])
    def get_all_users():
        users_dict = defaultdict(list)
        for user in query_db("select * from users"):
            users_dict[user["id"]].append(user)
            print(users_dict)
        return users_dict

    @app.route("/registerUser", methods=["POST"])
    def register_user():
        user_info = request.get_json(force=True)
        req_username = user_info["username"]
        req_difficulty_level = grade_to_difficulty_mapping.get(
            user_info["grade"])

        # below fields not needed as of now
        categories = user_info["categories"]
        initial_categories = ','.join(categories)
        categories_dict = {}
        for cat in categories:
            categories_dict[cat] = [0, 0, "notPass"]

        categories_string = str(categories_dict)
        print(categories_string)

        user = query_db(
            "select * from users where username = ?", [req_username], one=True
        )
        response = flask.Response()

        if user is None:
            print("No such user")
            try:
                insert_into_db(
                    "insert into users(username, difficulty_level, initial_categories ,categories, total_correct, total_incorrect) values (?,?,?,?,?,?)",
                    (req_username, req_difficulty_level,
                     initial_categories, categories_string, 0, 0),
                )
                response = jsonify("New user added")

            except sqlite3.IntegrityError as e:
                print("Error Occured: ", e)
                abort(400)

        else:
            response = jsonify(req_username, "has the id", user["id"])
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    # get existing user

    @app.route("/fetchUser", methods=["POST"])
    def fetch_user():
        user_info = request.get_json()
        req_username = user_info["username"]
        user = query_db(
            "select * from users where username = ?", [req_username], one=True
        )
        if user is None:
            print("No such user")
            return "User does not exist"
        else:
            print(req_username, "has the id", user["id"])
        return user

    # get json question data

    @app.route("/questionData", methods=["GET"])
    def question_data():
        f = open("data_handling/data.json")
        data = json.load(f)
        response = jsonify({"data": data})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    # get json categories
    @app.route("/getGradeCategories", methods=["POST"])
    def get_grade_categories():
        user_info = request.get_json(force=True)
        req_grade = user_info["grade"]
        grade = req_grade
        if req_grade.isnumeric() == False:
            grade = gradeMappings[req_grade]
        grade_cats = set()
        f = open("data_handling/data.json")
        data = json.load(f)
        for item in data:
            if item["grade"] == grade:
                grade_cats.add(item["category"])
        grade_cats = list(grade_cats)
        response = jsonify({"categories": list(grade_cats)})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    # get json questionnaire questions for new user

    @app.route("/pickQuestionnaireQuestions", methods=["GET"])
    def pick_questionnaire_questions():
        f = open("data_handling/data.json")
        data = json.load(f)
        questions = []
        for grade in grades:
            question = next(x for x in data if x["grade"] == grade)
            questions.append(question)
        response = jsonify({"data": questions})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    # method to store user responses in db

    def store_submissions(question, correct, username):
        question_id = question["skillno"]
        question_category = question["category"]
        question_difficulty = question["difficulty"]

        try:

            # update correct answers into correct_questions table
            if correct:
                insert_into_db(
                    "insert into correct_questions(username, question_id, difficulty_level, categories) values (?,?,?,?)",
                    (username, question_id, question_difficulty, question_category),
                )

            # update total_correct and total_incorrect answers in users table
            user = query_db(
                "select * from users where username = ?", [username], one=True
            )
            total_correct = int(user["total_correct"]) + (1 if correct else 0)
            total_incorrect = int(
                user["total_incorrect"]) + (1 if not correct else 0)
            update_db(
                "update users set total_correct=?,total_incorrect=? where username = ?",
                (total_correct, total_incorrect, username),
            )

            categories_dict = ast.literal_eval(user["categories"])
            if question_category in categories_dict:
                if correct:
                    categories_dict[question_category][0] += 1
                else:
                    categories_dict[question_category][1] += 1
            # else:
            #     if correct:
            #         categories_dict[question_category] = [1, 0, "notPass"]
            #     else:
            #         categories_dict[question_category] = [0, 1, "notPass"]

            # # new if else to check pass rate of each category
            # correctCount, falseCount = (
            #     categories_dict[question_category][0],
            #     categories_dict[question_category][1],
            # )
            # if correctCount + falseCount >= 10:
            #     user_category_score = correctCount / \
            #         (correctCount + falseCount)
            #     if user_category_score >= 0.5:
            #         categories_dict[question_category][2] = "pass"
            #     else:
            #         categories_dict[question_category][2] = "notPass"

            # pprint(categories_dict)

            # update categories column in users table
            update_db(
                "update users set categories=? where username = ?",
                (str(categories_dict), username),
            )

        except sqlite3.IntegrityError as e:
            print("Error Occured: ", e)
            pass

    # get json question choice
    @app.route("/pickQuestion", methods=["POST"])
    def pick_question():
        question_info = request.get_json(force=True)
        question = question_info["question"]
        correct = question_info["correct"]
        username = question_info["username"]

        question_category = question["category"]
        user = query_db("select * from users where username = ?",
                        [username], one=True)

        categories_dict = ast.literal_eval(user["categories"])

        # only store submission if questions were attempted
        if question:
            try:
                store_submissions(question, correct, username)
            except Exception as e:
                print(f"Exception Occured {e}")
                pass

        # get all correct questions attempted by user
        correct_question_ids = query_db(
            "select question_id from correct_questions where username = ?", [username])

        currUser_correctQuestions = [
            item["question_id"] for item in correct_question_ids
        ]

        user_data = query_db(
            "select * from users where username = ?", [username], one=True
        )

        # get user difficulty level
        user_difficulty_level = int(user_data["difficulty_level"])
        user_initial_category = user_data["initial_categories"]
        user_initial_category_list = user_initial_category.split(",")

        categories_dict = ast.literal_eval(user_data["categories"])
        print(categories_dict)
        # get all question data
        f = open("data_handling/data.json")
        data = json.load(f)

        # get all question ids of current difficulty level of user except the ones already attempted
        valid_question_ids = []
        for index, item in enumerate(data):
            if (
                (item["difficulty"] == user_difficulty_level)
                and (
                    item["category"] in categories_dict
                    and categories_dict[item["category"]][2] == "notPass"
                )
                and (item["skillno"] not in currUser_correctQuestions)
            ):
                valid_question_ids.append(index)
        print('valid_question_ids is: ', valid_question_ids)
        if valid_question_ids or len(valid_question_ids) != 0:
            next_index = random.choice(valid_question_ids)
        else:
            # if user has passed initial categories -> add the rest
            # if user has failed atleast 1 initial category -> downgrade to lower difficulty
            if len(categories_dict.keys()) == len(user_initial_category_list):
                have_passed_all_categories = True
                for idx, init_cat in enumerate(user_initial_category_list):
                    if init_cat not in categories_dict.keys():
                        continue
                    correct_answers = categories_dict[init_cat][0]
                    wrong_answers = categories_dict[init_cat][1]
                    score = correct_answers / (correct_answers + wrong_answers)

                    if score < 0.6:
                        have_passed_all_categories = False

                        delete_from_db("delete from correct_questions where username = ? AND difficulty_level = ?",
                                       (username, user_difficulty_level))

                        new_difficulty_level = user_difficulty_level - \
                            1 if user_difficulty_level > 1 else 1
                        print("DOWNGRADING USER DIFFICULTY LEVEL TO: ",
                              new_difficulty_level)
                        new_categories_dict = {}

                        # get categories iof new difficulty level
                        categories_of_new_difficulty_level = get_categories(
                            new_difficulty_level)

                        for cat in user_initial_category_list:
                            if cat in categories_of_new_difficulty_level:
                                new_categories_dict[cat] = [0, 0, "notPass"]
                            else:
                                new_categories_dict[random.choice(categories_of_new_difficulty_level)] = [
                                    0, 0, "notPass"]

                        update_db(
                            "update users SET difficulty_level=?, categories=? where username = ?",
                            (new_difficulty_level, str(
                                new_categories_dict), username),
                        )

                        updated_correct_question_ids = query_db(
                            "select question_id from correct_questions where username = ?", [username])
                        updated_currUser_correctQuestions = [
                            item["question_id"] for item in updated_correct_question_ids]

                        for index, item in enumerate(data):
                            if ((item["difficulty"] == user_difficulty_level)
                                and (
                               item["category"] in new_categories_dict
                               and new_categories_dict[item["category"]][2] == "notPass"
                               )
                                    and (item["skillno"] not in updated_currUser_correctQuestions)):
                                next_index = index
                                break

                        break

                    else:
                        categories_dict = categories_dict
                        categories_dict[init_cat][2] = "pass"
                        update_db(
                            "update users SET categories=? where username = ?",
                            (str(categories_dict), username),
                        )

                # outside for loop - either passed or not passed all categories
                if have_passed_all_categories:
                    # copy categories_dict to new_categories_dict
                    # new_categories_dict = copy.deepcopy(categories_dict)
                    all_categories_current_difficulty = get_categories(
                        user_difficulty_level)

                    # add all categories of current difficulty level to new_categories_dict if not already present
                    for cat in all_categories_current_difficulty:
                        if cat not in categories_dict.keys():
                            categories_dict[cat] = [0, 0, "notPass"]

                    # update user table
                    update_db(
                        "update users SET categories=? where username = ? and difficulty_level = ?",
                        (str(categories_dict), username, user_difficulty_level),
                    )

                    # pick next question
                    updated_correct_question_ids = query_db(
                        "select question_id from correct_questions where username = ?", [username])
                    updated_currUser_correctQuestions = [
                        item["question_id"] for item in updated_correct_question_ids]

                    for index, item in enumerate(data):
                        if ((item["difficulty"] == user_difficulty_level)
                            and (
                            item["category"] in categories_dict
                            and categories_dict[item["category"]][2] == "notPass"
                        )
                                and (item["skillno"] not in updated_currUser_correctQuestions)):
                            next_index = index
                            break

            # If I'm here, that means, user has passed all the categories of current difficulty level
            # if the only fails 1 category and has passed all the categories of current difficulty level, upgrade to next level
            # if the user fails 2 or more categories, downgrade to lower difficulty
            else:
                passed_all_categories = True
                failed_category_count = 0
                # for each user category, checking if the user passed or failed
                for category in categories_dict:
                    if category not in user_initial_category_list:
                        correct_answers, wrong_answers = categories_dict[
                            category][0], categories_dict[category][1]
                        score = correct_answers / \
                            (correct_answers + wrong_answers)

                        if score < 0.4:
                            # clear correct_questions table to current category and difficulty level
                            failed_category_count += 1
                            passed_all_categories = False

                            # delete correct questions history for curr difficulty level in DB
                            delete_from_db("delete from correct_questions where username = ? AND difficulty_level = ? AND categories = ?",
                                           (username, user_difficulty_level, category))

                            if failed_category_count > 1:
                                break

                            categories_dict[category][2] = "notPass"

                            # Update the category in the user table
                            update_db(
                                "update users SET categories=? where username = ?",
                                (str(categories_dict), username),
                            )
                            # clear attempted questions table to current category and difficulty level
                            # downgrade user if grade >1
                            # return index based on new difficulty level

                        else:
                            categories_dict[category][2] = "pass"
                            update_db(
                                "update users SET categories=? where username = ?",
                                (str(categories_dict), username),
                            )
                        # update user table
                if passed_all_categories or failed_category_count < 2:
                    new_difficulty_level = user_difficulty_level + \
                        1 if user_difficulty_level < 10 else print(
                            "Ran of difficulty levels")

                    new_diffculty_initial_cat = {}
                    all_categories_new_difficulty = get_categories(
                        new_difficulty_level)

                    for cat in user_initial_category_list:
                        if cat in all_categories_new_difficulty:
                            new_diffculty_initial_cat[cat] = [
                                0, 0, "notPass"]
                        else:
                            new_diffculty_initial_cat[random.choice(all_categories_new_difficulty)] = [
                                0, 0, "notPass"]

                    # set new difficulty level and categories
                    update_db(
                        "update users SET difficulty_level=?, categories=? where username = ?",
                        (new_difficulty_level, str(
                            new_diffculty_initial_cat), username),
                    )

                    # select next question
                    updated_correct_question_ids = query_db(
                        "select question_id from correct_questions where username = ?", [username])
                    updated_currUser_correctQuestions = [
                        item["question_id"] for item in updated_correct_question_ids]

                    for index, item in enumerate(data):
                        if ((item["difficulty"] == new_difficulty_level)
                            and (
                            item["category"] in new_diffculty_initial_cat
                            and new_diffculty_initial_cat[item["category"]][2] == "notPass"
                        )
                                and (item["skillno"] not in updated_currUser_correctQuestions)):
                            next_index = index
                            break

                else:
                    # downgade user if grade >1
                    delete_from_db("delete from correct_questions where username = ? AND difficulty_level = ?",
                                   (username, user_difficulty_level))

                    new_difficulty_level = user_difficulty_level - \
                        1 if user_difficulty_level > 1 else 1

                    new_categories_dict = {}

                    # get categories iof new difficulty level
                    categories_of_new_difficulty_level = get_categories(
                        new_difficulty_level)

                    for cat in user_initial_category_list:
                        if cat in categories_of_new_difficulty_level:
                            new_categories_dict[cat] = [0, 0, "notPass"]
                        else:
                            new_categories_dict[random.choice(categories_of_new_difficulty_level)] = [
                                0, 0, "notPass"]

                    update_db(
                        "update users SET difficulty_level=?, categories=? where username = ?",
                        (new_difficulty_level, str(
                            new_categories_dict), username),
                    )

                    updated_correct_question_ids = query_db(
                        "select question_id from correct_questions where username = ?", [username])
                    updated_currUser_correctQuestions = [
                        item["question_id"] for item in updated_correct_question_ids]

                    for index, item in enumerate(data):
                        if ((item["difficulty"] == user_difficulty_level)
                            and (
                            item["category"] in new_categories_dict
                            and new_categories_dict[item["category"]][2] == "notPass"
                        )
                                and (item["skillno"] not in updated_currUser_correctQuestions)):
                            next_index = index
                            break

        #  GRADE PICKING LOGIC
        total_attempted = user_data["total_correct"] + \
            user_data["total_incorrect"]

        if len(categories_dict) == len(user_initial_category_list) and total_attempted >= 3:
            has_failed_initial_cat = False
            has_passed_all_initial_cat = False
            for idx, each_cat in enumerate(categories_dict):
                print("In Grade Picking Logic")
                print('category: ', each_cat)

                total_attempted_per_category = categories_dict[each_cat][0] + \
                    categories_dict[each_cat][1]

                if total_attempted_per_category >= 3:
                    category_score = categories_dict[each_cat][0] / \
                        total_attempted_per_category
                    print('Inside if line 574 category_score: ', category_score)
                    if category_score > 0.6:
                        categories_dict[each_cat][2] = "pass"
                        if idx == len(categories_dict) - 1:
                            has_passed_all_initial_cat = True
                        update_db(
                            "update users SET categories=? where username = ?",
                            (str(categories_dict), username),
                        )
                    else:
                        print("Failing user in category: ", each_cat)
                        categories_dict[each_cat][2] = "notPass"
                        update_db(
                            "update users SET categories=? where username = ?",
                            (str(categories_dict), username),
                        )
                        has_failed_initial_cat = True
                        break

            if has_failed_initial_cat:
                print("DOWNGRADE USER IN GRADE PICKING LOGIC")
                # downgrade user if grade >1
                delete_from_db("delete from correct_questions where username = ? AND difficulty_level = ?",
                               (username, user_difficulty_level))

                new_difficulty_level = (
                    user_difficulty_level - 1) if user_difficulty_level > 1 else 1

                new_categories_dict = {}

                # get categories iof new difficulty level
                categories_of_new_difficulty_level = get_categories(
                    new_difficulty_level)

                for cat in user_initial_category_list:
                    if cat in categories_of_new_difficulty_level:
                        new_categories_dict[cat] = [0, 0, "notPass"]
                    else:
                        new_categories_dict[random.choice(categories_of_new_difficulty_level)] = [
                            0, 0, "notPass"]

                update_db(
                    "update users SET difficulty_level=?, categories=? where username = ?",
                    (new_difficulty_level, str(
                        new_categories_dict), username),
                )

                updated_correct_question_ids = query_db(
                    "select question_id from correct_questions where username = ?", [username])
                updated_currUser_correctQuestions = [
                    item["question_id"] for item in updated_correct_question_ids]

                for index, item in enumerate(data):
                    if ((item["difficulty"] == user_difficulty_level)
                        and (
                        item["category"] in new_categories_dict
                        and new_categories_dict[item["category"]][2] == "notPass"
                    )
                            and (item["skillno"] not in updated_currUser_correctQuestions)):
                        next_index = index
                        break

            if not has_failed_initial_cat and has_passed_all_initial_cat:
                # add remaining categories of curr difficult level to user profile
                all_categories_current_difficulty = get_categories(
                    user_difficulty_level)

                # add all categories of current difficulty level to new_categories_dict if not already present
                for cat in all_categories_current_difficulty:
                    if cat not in categories_dict.keys():
                        categories_dict[cat] = [0, 0, "notPass"]

                # update user table
                update_db(
                    "update users SET categories=? where username = ? and difficulty_level = ?",
                    (str(categories_dict), username, user_difficulty_level),
                )

                updated_correct_question_ids = query_db(
                    "select question_id from correct_questions where username = ?", [username])
                updated_currUser_correctQuestions = [
                    item["question_id"] for item in updated_correct_question_ids]

                # getting new next index
                for index, item in enumerate(data):
                    if ((item["difficulty"] == user_difficulty_level)
                        and (
                        item["category"] in categories_dict
                        and categories_dict[item["category"]][2] == "notPass"
                    )
                            and (item["skillno"] not in updated_currUser_correctQuestions)):
                        next_index = index
                        break

        if len(categories_dict) > len(user_initial_category_list) and total_attempted >= 40:
            # check if user has passed all categories or failed atleast 2
            failed_cat_count = 0
            for each_cat in categories_dict:
                total_attempted_per_category = categories_dict[each_cat][0] + \
                    categories_dict[each_cat][1]
                if total_attempted_per_category == 0:
                    continue
                category_score = categories_dict[each_cat][0] / \
                    total_attempted_per_category
                if category_score > 0.4:
                    categories_dict[each_cat][2] = "pass"
                    update_db(
                        "update users SET categories=? where username = ?",
                        (str(categories_dict), username),
                    )
                else:
                    categories_dict[each_cat][2] = "notPass"
                    update_db(
                        "update users SET categories=? where username = ?",
                        (str(categories_dict), username),
                    )
                    failed_cat_count += 1
                    if failed_cat_count >= 2:
                        break

            if failed_cat_count >= 2:
                # downgrade user if grade >1

                delete_from_db("delete from correct_questions where username = ? AND difficulty_level = ?",
                               (username, user_difficulty_level))

                new_difficulty_level = (
                    user_difficulty_level - 1) if user_difficulty_level > 1 else 1

                new_categories_dict = {}
                # get categories iof new difficulty level
                categories_of_new_difficulty_level = get_categories(
                    new_difficulty_level)

                for cat in user_initial_category_list:
                    if cat in categories_of_new_difficulty_level:
                        new_categories_dict[cat] = [0, 0, "notPass"]
                    else:
                        new_categories_dict[random.choice(categories_of_new_difficulty_level)] = [
                            0, 0, "notPass"]

                new_total_correct = 0
                new_total_incorrect = 0
                update_db(
                    "update users SET difficulty_level=?, categories=?, total_correct=?, total_incorrect=? where username = ?",
                    (new_difficulty_level, str(
                        new_categories_dict), new_total_correct, new_total_incorrect, username),
                )

                updated_correct_question_ids = query_db(
                    "select question_id from correct_questions where username = ?", [username])
                updated_currUser_correctQuestions = [
                    item["question_id"] for item in updated_correct_question_ids]

                for index, item in enumerate(data):
                    if ((item["difficulty"] == user_difficulty_level)
                        and (
                        item["category"] in new_categories_dict
                        and new_categories_dict[item["category"]][2] == "notPass"
                    )
                            and (item["skillno"] not in updated_currUser_correctQuestions)):
                        next_index = index
                        break

            else:
                # upgrade user to next difficulty level
                # assign initial categories

                new_difficulty_level = user_difficulty_level + \
                    1 if user_difficulty_level < 10 else print(
                        "Ran of difficulty levels")

                new_diffculty_initial_cat = {}
                all_categories_new_difficulty = get_categories(
                    new_difficulty_level)

                for cat in user_initial_category_list:
                    if cat in all_categories_new_difficulty:
                        new_diffculty_initial_cat[cat] = [
                            0, 0, "notPass"]
                    else:
                        new_diffculty_initial_cat[random.choice(all_categories_new_difficulty)] = [
                            0, 0, "notPass"]

                new_total_correct = 0
                new_total_incorrect = 0
                # set new difficulty level and categories
                update_db(
                    "update users SET difficulty_level=?, categories=?, total_correct=?, total_incorrect=? where username = ?",
                    (new_difficulty_level, str(
                        new_diffculty_initial_cat), new_total_correct, new_total_incorrect, username),
                )
                # select next question
                updated_correct_question_ids = query_db(
                    "select question_id from correct_questions where username = ?", [username])
                updated_currUser_correctQuestions = [
                    item["question_id"] for item in updated_correct_question_ids]

                for index, item in enumerate(data):
                    if ((item["difficulty"] == new_difficulty_level)
                        and (
                        item["category"] in new_diffculty_initial_cat
                        and new_diffculty_initial_cat[item["category"]][2] == "notPass"
                    )
                            and (item["skillno"] not in updated_currUser_correctQuestions)):
                        next_index = index
                        break

        # # do this for every 10th question attempted or when no more valid questions left in current grade
        # grade_change = "NONE"
        # if (
        #     total_attempted != 0 and total_attempted % 15 == 0 or not valid_question_ids
        # ):  # avoid division by 0
        #     grade_change = grade_reccomendation(
        #         user_data["total_correct"], total_attempted
        #     )
        #     update_user_grade(username, grade_change)

        response = jsonify({"index": next_index})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    def get_question_id(skill_no_str):
        keyword = "skillno="
        _, _, after_keyword = skill_no_str.partition(keyword)
        return int(after_keyword)

    # grade reccomendation logic

    def grade_reccomendation(total_correct, total_attempted):
        # This would recommend a newer or same grade depending on the win/loss rate.
        # If the user agrees to the next grade then the front end can request a question for grade+1 and category
        # we would also update the current grade and category of the user in the users table
        win_rate = total_correct / total_attempted

        if win_rate > 0.8:
            return "UPGRADE"

        elif win_rate < 0.25:
            return "DOWNGRADE"

        else:
            return "NONE"

    # grade update based on user response
    def update_user_grade(username, grade_change):
        user = query_db("select * from users where username=?",
                        [username], one=True)

        difficulty_level = user["difficulty_level"]
        total_correct = user["total_correct"]
        total_incorrect = user["total_incorrect"]

        if grade_change == "UPGRADE":
            difficulty_level += 1
            total_correct = 0
            total_incorrect = 0
        elif grade_change == "DOWNGRADE":
            difficulty_level -= 1
            total_correct = 0
            total_incorrect = 0

        # else no change for no grade update by user
        if grade_change != "NONE":
            update_db(
                "update users set difficulty_level=?,total_correct=?,total_incorrect=? where username = ?",
                (difficulty_level, total_correct, total_incorrect, username),
            )
        return "Update Successful"

    # get attempted questiond for a user
    # for debugging

    @app.route("/getAttemptedQuestions", methods=["POST"])
    def attempted_questions():
        req = request.get_json()
        username = req["username"]
        user_attempted_questions = query_db(
            "select * from correct_questions where username=?", [username]
        )
        print(user_attempted_questions)
        if user_attempted_questions is None:
            return "No questions attempted"

        response = jsonify(user_attempted_questions)
        response.headers.add("Access-Control-Allow-Origin", "*")
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

    def delete_from_db(query, args=()):
        conn = db.get_db()
        cur = conn.execute(query, args)
        conn.commit()
        cur.close()

    from . import db

    db.init_app(app)

    return app
