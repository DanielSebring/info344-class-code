# PHP Language and Runtime Day

Use this folder for the code we write during our PHP Language and Runtime day.

After I lead you through the introduction, I'll let you practice by completing the following micro-challenges. These are not graded, but they will help prepare you to do the graded LAMP challenge.

You may want to refer to my [Intro to PHP tutorial](https://info344.ischool.uw.edu/course/tutorials/php-intro), as well as the [PHP documentation](https://secure.php.net/manual/en/). 

## Simple Warm-Up

In a new PHP script named `warmup.php`:
- declare a variable and initialize it to a random integer between 1 and 100
- echo that value, embedding it in the message "your new random value is nnn", using an interpolated string. For example, if the new random number was 50, your message should say "your new random value is 50". You should also embed a newline character so that the next prompt appears on the next line in the terminal.

To figure out how to generate a random integer, search for "php random integer" and read what you find.

run your page by executing this in the terminal:
```bash
$ php warmup.php
```

## Arrays and Loops

Write a script that builds an ordered array of month names in calendar order, and then iterates the array, echoing each month name. Try to build the array by using the date functions to generate the month names in calendar order, instead of just hardcoding them. 

Then sort the month names aphabetically and re-iterate and echo the array. 

## API Request

Write a PHP page named `weather.php` that requests the following URL, and embeds the current temperature and weather description into a simple HTML page.

```
http://api.openweathermap.org/data/2.5/weather?q=Seattle,us&units=imperial&appid=2de143494c0b295cca9337e1e96b00e0
```  

This is an API that responds with JSON. You should [open it in your browser](http://api.openweathermap.org/data/2.5/weather?q=Seattle,us&units=imperial&appid=2de143494c0b295cca9337e1e96b00e0) to see what the response JSON looks like.

To test this, start a PHP server in the directory where this page lives:

```bash
$ php -S localhost:9000
```

and then open [http://localhost:9000/weather.php](http://localhost:9000/weather.php) in your browser.

If you get that working, allow the client to use a query string parameter to name the city and country.

Or use PHP to get the IP Address of the client, and call the [IP location API](http://ip-api.com/docs/api:json) to get the location information for that IP address. Then you can call the Open Weather API for that location, returning the current weather for wherever the client happens to be (or at least where the source IP was--if they go through a proxy or VPN server, that's the IP your server will get) 

## Keep Going

If you get through all of these, keep thinking of other little challenges you can do, or explore some more of the [built-in functions](http://php.net/manual/en/funcref.php).

I will show you how to interact with databases during our next class.
