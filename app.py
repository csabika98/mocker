from flask import Flask, render_template, request, Response, jsonify, redirect, url_for
from waitress import serve
import json
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Variables for storing response data
response_data = {}
response_code = 200
content_type = 'application/json'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api', methods=['POST'])
def api():
    global response_data, response_code, content_type

    request_type = request.form['request_type']
    request_content = request.form['request_data']
    response_code = int(request.form['response_code'])

    if request_type == 'JSON':
        try:
            json_request = json.loads(request_content)
            response_data = {
                'data': json_request,
                'content_type': 'application/json',
                'code': response_code
            }
        except json.JSONDecodeError as e:
            return jsonify(error=f"Invalid JSON request: {str(e)}"), 400
    elif request_type == 'XML':
        try:
            xml_request = ET.fromstring(request_content)
            response_data = {
                'data': request_content,
                'content_type': 'application/xml',
                'code': response_code
            }
        except Exception as e:
            return jsonify(error=f"Invalid XML request: {str(e)}"), 400

    return redirect(url_for('get_response'))

@app.route('/get_response', methods=['GET', 'POST', 'PUT', 'UPDATE', 'DELETE'])
def get_response():
    global response_data

    if response_data:
        response_content = response_data.get('data', '')
        response_code = response_data.get('code', 404)
        content_type = response_data.get('content_type', 'application/json')

        if isinstance(response_content, dict):
            response_content = json.dumps(response_content)

        return Response(response_content, content_type=content_type, status=response_code)

    return jsonify(error='No response data available'), 404

def run_server():
    serve(app, host="localhost", port=5000)

if __name__ == '__main__':
    run_server()
    print("Server is started. API endpoint: http://localhost:5000/")

