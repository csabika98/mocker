import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import ttk
import json
import xml.etree.ElementTree as ET
from flask import Flask, request, Response
from waitress import serve
import threading
import os
import sys

# Create the desktop app UI
window = tk.Tk()
window.title("Mockup Server")
window.geometry("823x678")

# Flask app and server variables
app = None
server_thread = None
server_running = False

# Text widget for JSON or XML input
text_widget = scrolledtext.ScrolledText(window, width=80, height=30)
text_widget.pack()

# Entry field for the HTTP response code
response_code_label = ttk.Label(window, text="Response Code:")
response_code_label.pack()
response_code_entry = ttk.Entry(window)
response_code_entry.insert(0, "200")
response_code_entry.pack()

# Create a dropdown to select the request type
request_type_label = ttk.Label(window, text="Request Type:")
request_type_label.pack()
request_type_var = tk.StringVar()
request_type_var.set("JSON")  # Default request type is JSON
request_type_dropdown = ttk.Combobox(window, textvariable=request_type_var, values=["JSON", "XML"])
request_type_dropdown.pack()

# Function to send the request (with JSON and XML support)
def send_request():
    global app, server_thread, server_running

    if server_running:
        return

    # Get the request data from the text widget
    request_data = text_widget.get("1.0", tk.END).strip()

    # Get the HTTP response code from the entry field
    response_code = int(response_code_entry.get())

    # Determine the request type (JSON or XML)
    request_type = request_type_var.get()

    if request_type == "JSON":
        try:
            # Attempt to parse the input as JSON
            json_request = json.loads(request_data)
            content_type = 'application/json'
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON request: {str(e)}")
            return
        response_data = json_request
    elif request_type == "XML":
        try:
            # Attempt to parse the input as XML
            xml_request = ET.fromstring(request_data)
            content_type = 'application/xml'
        except Exception as e:
            messagebox.showerror("Error", f"Invalid XML request: {str(e)}")
            return
        response_data = request_data

    if server_thread and server_thread.is_alive():
        server_thread.join()

    app = Flask(__name__)

    @app.route("/api", methods=["POST"])
    def api():
        if request_type == "JSON":
            response_headers = [('Content-type', 'application/json')]
            return Response(json.dumps(response_data), content_type='application/json', status=response_code, headers=response_headers)
        if request_type == "XML":
            response_headers = [('Content-type', 'application/xml')]
            return Response(response_data, content_type=content_type, status=response_code, headers=response_headers)

    def run_server():
        serve(app, host="localhost", port=5000)

    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    status_label.config(text="Server is started. API endpoint: http://localhost:5000/api")
    server_running = True

# Function to save and restart the application
def save_and_restart():
    response_content = text_widget.get("1.0", tk.END)
    response_code = response_code_entry.get()

    with open("saved_response.txt", "w") as file:
        file.write(response_code + "\n")
        file.write(response_content)

    python = sys.executable
    os.execl(python, python, *sys.argv)

# Function to load the saved response
def load_saved_response():
    try:
        with open("saved_response.txt", "r") as file:
            response_code = file.readline().strip()
            response_content = file.read()
            response_code_entry.delete(0, tk.END)
            response_code_entry.insert(0, response_code)
            text_widget.delete("1.0", tk.END)
            text_widget.insert(tk.END, response_content)
    except FileNotFoundError:
        messagebox.showerror("Error", "No saved response found.")

# Create a "Send Request" button
send_button = ttk.Button(window, text="Send Request", command=send_request)
send_button.pack()

# Create a button to save and restart the application
restart_button = ttk.Button(window, text="Save and Restart", command=save_and_restart)
restart_button.pack()

# Create a label to display the server status
status_label = ttk.Label(window, text="")
status_label.pack()

# Load the saved response when the application starts
load_saved_response()

# Run the desktop app UI
window.mainloop()
