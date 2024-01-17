from flask import Flask, render_template, request, Response, jsonify, redirect, url_for
from waitress import serve
import json
import xml.etree.ElementTree as ET
import sqlite3


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Set a secret key for sessions

# SQLite3 database setup
DATABASE = 'responses.db'

def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            content_type TEXT,
            response_code INTEGER
        )
    ''')
    conn.commit()
    conn.close()

create_table()



# Variables for storing response data
response_data = {}
response_code = 200
content_type = 'application/json'

@app.route('/')
def index():
    return render_template('index.html')


latest_response_id = 1


@app.route('/api', methods=['POST'])
def api():
    global response_code, content_type, latest_response_id

    request_type = request.form['request_type']
    request_content = request.form['request_data']
    response_code = int(request.form['response_code'])

    if request_type == 'JSON':
        try:
            json_request = json.loads(request_content)
            save_response_to_db(json_request, 'application/json', response_code)
        except json.JSONDecodeError as e:
            return jsonify(error=f"Invalid JSON request: {str(e)}"), 400
    elif request_type == 'XML':
        try:
            xml_request = ET.fromstring(request_content)
            save_response_to_db(request_content, 'application/xml', response_code)
        except Exception as e:
            return jsonify(error=f"Invalid XML request: {str(e)}"), 400


    latest_response_id += 1
    ##return redirect(url_for('get_response'))
    return jsonify(message='Request received successfully', latest_response_id=latest_response_id)


def save_response_to_db(data, content_type, response_code):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO responses (data, content_type, response_code)
        VALUES (?, ?, ?)
    ''', (json.dumps(data) if isinstance(data, dict) else data, content_type, response_code))
    conn.commit()
    conn.close()


@app.route('/get_response', methods=['GET', 'POST', 'PUT', 'UPDATE', 'DELETE'])
def get_response():
    response_id = request.args.get('id')
    if response_id:
        response_data = fetch_response_from_db(response_id)
        if response_data:
            response_content = response_data[0]
            content_type = response_data[1]
            response_code = response_data[2]

            return Response(response_content, content_type=content_type, status=response_code)

    return jsonify(error='No response data available'), 404

def fetch_response_from_db(response_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT data, content_type, response_code FROM responses WHERE id = ?', (response_id,))
    response_data = cursor.fetchone()
    conn.close()
    print(response_data)
    return response_data

@app.route('/get_latest_response_id', methods=['GET'])
def get_latest_response_id():
    global latest_response_id
    return jsonify(latest_response_id=latest_response_id)


def run_server():
    serve(app, host="localhost", port=5000)

if __name__ == '__main__':
    run_server()
    print("Server is started. API endpoint: http://localhost:5000/")

