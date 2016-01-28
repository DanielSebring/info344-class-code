'use strict';

var connPool;

var stories = {
	//getAll: function() {}
	getAll() {
		var sql = `select * from stories 
			order by votes desc, createdOn desc limit 50`;
		return connPool.queryAsync(sql);
	},
	
    get(id) {
        var sql = 'select * from stories where id=?';
        return connPool.queryAsync(sql, [id])
            .then(function(rows) {
                return rows.length > 0 ? rows[0] : null;
            });
    },
    
	insert(story) {
        //validate data
        var sql = `insert into stories (url, title) values (?, ?)`;
		var params = [story.url, story.title];
        return connPool.queryAsync(sql, params)
            .then(function(results) {
                return stories.get(results.insertId);
            });
        //things
    },
	
	upVote(id) {
		var sql = 'update stories set votes=votes+1 where id=?';
		var params = [id];
		return connPool.queryAsync(sql, params)
			.then(function(results) {
					sql = 'select * from stories where id=?';
					return connPool.queryAsync(sql, params);
			})
			.then(function(rows) {
				return rows.length > 0 ? rows[0] : null;
			});
	}
};

module.exports.Model = function(connectionPool) {
	connPool = connectionPool;
	return stories;
}