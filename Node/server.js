const sqlite3 = require('sqlite3').verbose();
const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const multer = require('multer');
const upload = multer({ storage: multer.memoryStorage() });
const spawn = require('child_process').spawn;

const app = express();
const port = 80;

let db = new sqlite3.Database('./targets.db', (err) => {
	if (err) {
		console.error(err.message);
	}
	console.log('loaded targets db');
});

app.use(bodyParser.urlencoded({extended:true}));
app.use(bodyParser.json());

app.listen(port, () => {
	console.log('web listener set up on ' + port);
});

app.get('/', (req, res) => {
	res.sendFile(path.join(__dirname + '/index.html'));
});

app.get('/api/', (req, res) => {
	let lastupdate = 0;
	if (req.query.lastupdate) {
		lastupdate = parseInt(req.query.lastupdate);
		if (isNaN(lastupdate)) {
			lastupdate = 0;
		}
	}

	let data = {image_updates:[], target_updates:[]};
	let sql = 'SELECT last_name lname, first_name fname, is_target is_t ' +
	      	  'FROM targets WHERE last_updated >= ' + lastupdate;
	db.all(sql, [], (err, rows) => {
        	if (err) {
                	throw err;
	        }
        	rows.forEach((row) => {
			let curJSON = {};
			curJSON['last_name'] = row.lname;
			curJSON['first_name'] = row.fname;
			curJSON['is_target'] = row.is_t;

                	data.target_updates.push(curJSON);
        	});
		sql = 'SELECT last_name lname, first_name fname ' +
              	      'FROM images WHERE last_updated >= ' + lastupdate;
	        db.all(sql, [], (err, rows) => {
        	        if (err) {
        	                throw err;
        	        }
        	        rows.forEach((row) => {
                	        curJSON = {};
                	        curJSON['last_name'] = row.lname;
                	        curJSON['first_name'] = row.fname;

	                        data.image_updates.push(curJSON);
	                });
			res.json(data);
	        });

	});
});

app.get('/api/images/', (req, res) => {
        let data = {images:[]};
        let sql = 'SELECT image1 img1, image2 img2, image3 img3, ' +
		  'image4 img4, image5 img5, image6 img6 ' +
                  'FROM images WHERE last_name = ? and first_name = ?';
	let imagenum = 0;
        if (req.query.imagenum) {
		if (req.query.imagenum == 'all') {
			imagenum = 'all'
		} else {
	                imagenum = parseInt(req.query.imagenum);
        	        if (isNaN(imagenum)) {
                	        imagenum = 0;
               		}
		}
        }

        db.all(sql, [req.query.lname, req.query.fname], (err, rows) => {
                if (err) {
                        throw err;
                }
                rows.forEach((row) => {
                        let curJSON = {};

			let i;
			for (i = 0; i < 6; i++) {
				data.images.push(null);
			}
			switch(imagenum) {
				case 'all':
					data.images[0] = row.img1;
                                        data.images[1] = row.img2;
                                        data.images[2] = row.img3;
                                        data.images[3] = row.img4;
                                        data.images[4] = row.img5;
                                        data.images[5] = row.img6;
					break;
				case 0:
					data.images[0] = row.img1;
					break;
                                case 1:
                                        data.images[1] = row.img1;
                                        break;
                                case 2:
                                        data.images[2] = row.img1;
                                        break;
                                case 3:
                                        data.images[3] = row.img1;
                                        break;
                                case 4:
                                        data.images[4] = row.img1;
                                        break;
                                case 5:
                                        data.images[5] = row.img1;
                                        break;

			}
                });
		res.json(data);
        });
});


app.post('/api/', upload.array('imgs',6), (req, res) => {
	console.log(req.body);
	console.log(req.files);
	let result = false;
	if (req.body.operation) {
		if (req.body.operation == 'update_target') {
			if (req.body.value && req.body.fname && req.body.lname) {
				let newValue = parseInt(req.body.value);
	                        if (newValue != 0) {
					newValue = 1;
        	                }
				let time = (new Date).getTime();
                	        let sql = 'UPDATE targets SET is_target = ?, ' +
				      'last_updated = ? WHERE last_name = ? and ' +
				      'first_name = ?';
				db.all(sql, [newValue, time,
					     req.body.lname,
					     req.body.fname], (err, rows) => {
			                if (err) {
                        			throw err;
			                }
					console.log('UPDATED ' +
						req.body.lname + ', ' +
						req.body.fname + ' TO ' +
						((newValue) ? 'TARGET' : 'NOT TARGET') +
						' AT ' + time);
				});
				result = true;
			}
		} else if (req.body.operation == 'new_target') {
			if (req.body.fname && req.body.lname && req.files && req.files.length == 6) {
				let time = (new Date).getTime();
				let sql = 'REPLACE INTO images (last_name, first_name, ' +
                                      'last_updated, image1, image2, image3, image4, image5, image6) ' +
				      'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)';
				db.all(sql, [req.body.lname, req.body.fname, time,
					     req.files[0].buffer.toString('base64'), req.files[1].buffer.toString('base64'),
					     req.files[2].buffer.toString('base64'), req.files[3].buffer.toString('base64'),
					     req.files[4].buffer.toString('base64'), req.files[5].buffer.toString('base64')],
				       (err, rows) => {
					if (err) {
						throw err;
					}
					console.log('ADDED ' +
						req.body.lname + ', ' +
						req.body.fname + ' WITH NEW IMAGES ');
				});
				sql = 'REPLACE INTO targets (last_name, first_name, last_updated) ' +
                                      'VALUES (?, ?, ?)';
				db.all(sql, [req.body.lname, req.body.fname, time], (err, rows) => {
                                        if (err) {
                                                throw err;
                                        }
                                });

				result = true;

			}
		}
	}
	res.json({success: result});;
});



//db.close()
