CREATE DATABASE info344chat;

USE info344chat;

CREATE TABLE message (
    id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nickname char(50),
    content TEXT NOT NULL,
<<<<<<< HEAD
    sent_timestamp TIMESTAMP
=======
    sent_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
>>>>>>> 5b8ba60135027c95d3a0d5568ffd4ab002ac878b
);

INSERT INTO message (nickname, content)
VALUES
    (NULL, "Hello, world!"),
    ("john doe", "Hi there...")
