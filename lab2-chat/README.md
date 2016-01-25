# Lab 2: Simple Chat Client Using PHP & MySQL

Let's get some practice using PHP's PDO to query and insert items into a
<<<<<<< HEAD
database. We will build a simple chat client for that will allow you to send
and receive messages with your classmates!
=======
database. We will build a simple chat client for this lab that will allow you
to send and receive messages with your classmates!
>>>>>>> 5b8ba60135027c95d3a0d5568ffd4ab002ac878b

## User Interface & Interactions

For the first part of this assignment, we will begin with a simple UI. When
users enter the chat, they should be able to see the last 10 messages sent.
Each message entry should display the nickname of the sender, the content of
the message, and the date/time in which it was sent.

<<<<<<< HEAD
Below the message list, provide the users with a textbox to specify a
nickname to send the message with and a textarea for the contents of the
=======
Below the message list, provide the users with a textbox to specify their
nickname to send the messages with, and a textarea for the contents of the
>>>>>>> 5b8ba60135027c95d3a0d5568ffd4ab002ac878b
message. They user should be able to send the message by pressing the enter key
or by clicking a "send" button next to the textarea. If the user does not
specify a nickname while sending a message, it should appear as 'anonymous'.

After sending a message, the page should refresh and show the newly sent
message in the page. If the user specified a nickname, ensure that it appears
in the newly loaded page to avoid re-entering.

## Our Database

Before we discuss how to connect to interact with our database, let's get a
<<<<<<< HEAD
better feel for MySQL directly from the command line! Run this command to get
into our database that's hosted on Digital Ocean:

```sql
mysql info344chat -h 159.203.233.236 -u info344student -p

show tables;
```

Your job is to write a query to fetch the last 10 messages, and another query
to insert a message into the 'message' table.
=======
better feel for MySQL directly from the command line!

TODO(nadavash): Finish this section.
>>>>>>> 5b8ba60135027c95d3a0d5568ffd4ab002ac878b

## Connecting to MySQL from PHP

We've already created a MySQL database with the necessary schema for you, so
all you need to do is connect and query it! You will need to make use of PHP's
PDO to interact with our database. Setting up the PDO looks something like this:

```php
<<<<<<< HEAD
$dbConn = new PDO("mysql:host=159.203.233.236;dbname=info344chat", "info344student", "***")
=======
$dbConn = new PDO("url:port", "username", "pass")
>>>>>>> 5b8ba60135027c95d3a0d5568ffd4ab002ac878b
```

Then you can use ```$dbConn``` to interact with our database. For more help
with using PDO, go to PHP's official documentation:

http://php.net/manual/en/book.pdo.php

<<<<<<< HEAD
## If you finish early...

Ask Nadav/David for more features to add to the chat!
=======
TODO(nadavash): Finish this section.
>>>>>>> 5b8ba60135027c95d3a0d5568ffd4ab002ac878b
