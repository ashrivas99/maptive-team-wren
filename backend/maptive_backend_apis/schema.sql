DROP TABLE IF EXISTS users;
-- DROP TABLE IF EXISTS user_model;
DROP TABLE IF EXISTS attempted_questions;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  difficulty_level INTEGER,
  total_correct INTEGER NOT NULL DEFAULT 0,
  total_incorrect INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE attempted_questions (
    username TEXT NOT NULL,
    question_id TEXT UNIQUE NOT NULL,
    answered_correctly INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT pk_attempted_questions PRIMARY KEY (username, question_id)
);

