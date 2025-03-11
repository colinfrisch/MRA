-- schema.sql
DROP TABLE IF EXISTS trainings;

DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    phone TEXT NOT NULL,
    current_training TEXT, -- storing JSON as TEXT
    finished_training TEXT -- storing JSON as TEXT
);

CREATE TABLE IF NOT EXISTS trainings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    field TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    content TEXT NOT NULL,
    question TEXT NOT NULL, 
    answers TEXT NOT NULL, -- storing JSON as TEXT
    training_id INTEGER NOT NULL,
    FOREIGN KEY(training_id) REFERENCES trainings(id)
);