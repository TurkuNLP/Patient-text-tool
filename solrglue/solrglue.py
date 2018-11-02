import requests
from flask import Flask, request, send_from_directory, send_file, g
from flask_cors import CORS
import csv
import logging
import json
import sqlite3 as sql

app = Flask(__name__)
CORS(app, resources=r'/*')
DATABASE = "data/annotations.db"

# This returns the database connection instance for the current request/application context using the g object,
# which is created at the start of a request and destroyed at the end.
# The sqlite3 library refuses to share a connection instances between requests to avoid dealing with concurrency issues.
def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sql.connect(DATABASE)
	return db

# This is to close a database connection when the request finishes/application context closes.
# More info in flask docs.
@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()


#@app.route('/solr/core1/select', methods=['GET','POST'])
#def forward_select():
#	if request.method == 'POST':
#		post_data = dict(request.form)
#		r = requests.post("http://localhost:8983" + request.full_path, data=post_data)
#		return json.dumps(r.json())
#	elif request.method == 'GET':
#		r = requests.get("http://localhost:8983" + request.full_path)
#		return json.dumps(r.json())

@app.route('/annotations_to_csv', methods=['GET'])
def annotations_to_csv():
	connection = get_db()
	with open('/tmp/solrglue.csv', 'w', newline='') as csv_file:
		csv_writer = csv.writer(csv_file)
		csv_writer.writerow(["teksti_numero","kommentti","valittu teksti","range_start","range_end"])
		for row in connection.execute("SELECT doc_id, comment, selected_text, range_start, range_end FROM annotations"):
			csv_writer.writerow(row)
	return send_file('/tmp/solrglue.csv', cache_timeout=0)

@app.route('/get_annotations', methods=['POST'])
def get_annotations():
	connection = get_db()
	data = request.form
	results = []
	for row in connection.execute("SELECT range_start, range_end, comment FROM annotations WHERE doc_id=?", (data["doc_id"],) ):
		results.append({"range_start": row[0], "range_end": row[1],"comment": row[2]})
	return json.dumps(results)

@app.route('/add_annotation', methods=['POST'])
def add_annotation():
	connection = get_db()
	data = request.form
	connection.execute("INSERT INTO annotations VALUES(?,?,?,?,?)",
						(data["doc_id"], data["range_start"], data["range_end"], data["comment"], data["selected_text"]) )
	connection.commit()
	return json.dumps("OK")

@app.route('/del_annotation', methods=['POST'])
def del_annotation():
	connection = get_db()
	data = request.form
	connection.execute("DELETE FROM annotations WHERE doc_id=? AND range_start=? AND range_end=?",
						(data["doc_id"], data["range_start"], data["range_end"]) )
	connection.commit()
	return json.dumps("OK")

@app.route('/mod_annotation', methods=['POST'])
def mod_annotation():
	connection = get_db()
	data = request.form
	connection.execute("UPDATE annotations SET comment=? WHERE doc_id=? AND range_start=? AND range_end=?",
						(data["comment"], data["doc_id"], data["range_start"], data["range_end"]) )
	connection.commit()
	return json.dumps("OK")

@app.route('/get_completed', methods=['POST'])
def get_completed():
	connection = get_db()
	data = request.form
	for row in connection.execute("SELECT EXISTS(SELECT 1 FROM completed_documents WHERE doc_id=?);", (data["doc_id"],) ):
		return json.dumps(row[0])

@app.route('/set_completed', methods=['POST'])
def set_completed():
	connection = get_db()
	data = request.form
	connection.execute("INSERT INTO completed_documents VALUES(?)", (data["doc_id"],) )
	connection.commit()
	return json.dumps("OK")

@app.route('/set_not_completed', methods=['POST'])
def set_not_completed():
	connection = get_db()
	data = request.form
	connection.execute("DELETE FROM completed_documents WHERE doc_id=?", (data["doc_id"],) )
	connection.commit()
	return json.dumps("OK")

@app.route('/js/<path:path>', methods=['GET'])
def get_rangy(path):
	return send_from_directory('js', path)

@app.route('/<path:path>', methods=['POST','GET'])
def forward_other(path):
	post_data = dict(request.form)
	if request.method == 'POST':
		r = requests.post("http://localhost:8983/" + request.full_path, data=post_data)
		return json.dumps(r.json())
	elif request.method == 'GET':
		r = requests.get("http://localhost:8983" + request.full_path)
		return json.dumps(r.json())
