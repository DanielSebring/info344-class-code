'use strict';

var express = require('express');
var morgan = require('morgan');
var bodyParser = require('body-parser');
var mysql = require('mysql');
var dbConfig = require('./secret/config-maria.json');
var bluebird = require('bluebird');

//create connection pool to MariaDV server
//
//
var connPool = bluebird.promisifyAll(mysql.createPool(dbConfig));
//require out stories controller
var storiesApi = require('./controllers/stories-api');
//require out story model
var stories = require('./models/stories.js').Model(connPool);

//create express application
var app = express();

//log request
app.use(morgan('dev'));
//parse JSON in the request body
app.use(bodyParser.json());

//serve static files from the /static subdir
app.use(express.static(__dirname + '/static'));

//mount the sorties api router under /api/v1
app.use('/api/v1', storiesApi.Router(stories));
//app.use('/controllers/stories-api.js', storiesApi.Router(Story));

app.listen(80, function() {
	console.log('server is listening...');
});