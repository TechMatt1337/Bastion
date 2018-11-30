const sqlite3 = require('sqlite3').verbose();
const express = require('express');

const app = express();
const port = 80;

let db = new sqlite3.Database('./targets.db', (err) => {
	if (err) {
		console.error(err.message);
	}
	console.log('loaded targets db');
});

app.listen(port, () => {
	console.log('web listener set up on ' + port);
});

app.get('/', (req, res) => {
	res.send("HELLO WORLD 1");
});

app.get('/api/', (req, res) => {
	lastupdate = 0;
	if (req.query.lastupdate) {
		lastupdate = parseInt(req.query.lastupdate, 10);
	}
	data = {targets:[]};
	sql = 'SELECT last_name lname, first_name fname, is_target is_t, ' +
	      'image1 img1, image2 img2, image3 img3 FROM targets ' +
	      'WHERE when_added >= ' + lastupdate;
	db.all(sql, [], (err, rows) => {
        	if (err) {
                	throw err;
	        }
        	rows.forEach((row) => {
			curJSON = {};
			curJSON['last_name'] = row.lname;
			curJSON['first_name'] = row.fname;
			curJSON['is_target'] = row.is_t;
			curJSON['image1'] = row.img1;
			curJSON['image2'] = row.img2;
			curJSON['image3'] = row.img3;
                	data.targets.push(curJSON);
        	});
		res.send(data);
	});
});


//db.close()
