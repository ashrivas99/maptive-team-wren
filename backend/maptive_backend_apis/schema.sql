DROP TABLE IF EXISTS users;
-- DROP TABLE IF EXISTS user_model;
DROP TABLE IF EXISTS correct_questions;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  difficulty_level INTEGER,
  initial_categories TEXT,
  categories TEXT,
  total_correct INTEGER NOT NULL DEFAULT 0,
  total_incorrect INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE correct_questions (
    username TEXT NOT NULL,
    question_id TEXT NOT NULL,
    difficulty_level INTEGER,
    categories TEXT,
    CONSTRAINT pk_attempted_questions PRIMARY KEY (username, question_id)
);

