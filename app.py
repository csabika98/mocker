from flask import Flask, render_template, request, Response, jsonify, redirect, url_for
from waitress import serve
import threading
import json
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Variables for storing response data
response_data = None
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
    res_code=request.form['response_code']

    if request_type == 'JSON':
        try:
            json_request = json.loads(request_content)
        except json.JSONDecodeError as e:
            return jsonify(error=f"Invalid JSON request: {str(e)}"), 400
        response_data = json_request
        content_type = 'application/json'
    elif request_type == 'XML':
        try:
            xml_request = ET.fromstring(request_content)
        except Exception as e:
            return jsonify(error=f"Invalid XML request: {str(e)}"), 400
        response_data = request_content
        content_type = 'application/xml'

    return redirect(url_for('get_response', response_code=res_code))


    
@app.route('/get_response', methods=['GET', 'POST', 'PUT', 'UPDATE', 'DELETE'])
def get_response():
    global response_data, response_code, content_type

    if response_data is not None:
        response_code = request.args.get('response_code', response_code)
        if content_type == 'application/json':
            return Response(json.dumps(response_data), content_type=content_type, status=response_code)
        elif content_type == 'application/xml':
            return Response(response_data, content_type=content_type, status=response_code)

    return jsonify(error='No response data available'), 404

def run_server():
    serve(app, host="localhost", port=5000)

if __name__ == '__main__':
    #server_thread = threading.Thread(target=run_server)
    #server_thread.daemon = True
    #server_thread.start()
    run_server()
    print("Server is started. API endpoint: http://localhost:5000/")
