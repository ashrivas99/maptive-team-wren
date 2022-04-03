DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS user_model;
DROP TABLE IF EXISTS attempted_questions;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  user_grade INTEGER,
  user_categories TEXT,
--   user_categories is a comma seperated string
  questionnaire_filled TEXT,
  current_category TEXT
);

CREATE TABLE user_model (
  username TEXT UNIQUE NOT NULL,
  category_attempted TEXT NOT NULL,
  grade_attempted TEXT NOT NULL,
  difficulty INTEGER NOT NULL,
  total_correct INTEGER NOT NULL DEFAULT 0,
  total_wrong INTEGER NOT NULL DEFAULT 0,
  CONSTRAINT pk_user_model PRIMARY KEY (username, category_attempted, grade_attempted)
);

CREATE TABLE attempted_questions (
    username TEXT UNIQUE NOT NULL,
    question_id TEXT UNIQUE NOT NULL,
    answered_correctly INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT pk_attempted_questions PRIMARY KEY (username)
);

