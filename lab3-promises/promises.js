'use strict';

var promise = new Promise(function (resolve, reject) {
	resolve(5);
});

promise.then(function(val) {
	console.log(val);
	return val + 1;
}).then(function(val) {
	console.log(val);
});