import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# Load symptoms and solutions from database.txt
def load_database():
    try:
        with open('database.txt', 'r') as file:
            data = json.load(file)
            return data.get("firstAidDatabase", [])
    except FileNotFoundError:
        print("database.txt not found. Please ensure it is in the same directory as server.py.")
        return []

first_aid_database = load_database()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"Requested path: {self.path}")
        if self.path == '/':
            self.path = '/indexf.html'
        elif self.path == '/symptoms':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            symptoms = [item["situation"] for item in first_aid_database]
            self.wfile.write(json.dumps({"symptoms": symptoms}).encode('utf-8'))
        else:
            file_path = self.path[1:]
            print(f"Checking file: {file_path}, Exists: {os.path.exists(file_path)}")
            try:
                with open(file_path, 'rb') as file:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(file.read())
            except FileNotFoundError:
                print(f"File not found: {file_path}")
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'File not found')

    def do_POST(self):
        if self.path == '/first-aid':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            print(f"Received POST data: {post_data}")
            try:
                data = json.loads(post_data)
                symptom = data.get('symptom', '')
                answer = data.get('answer', None)  # Allow answer to be None

                # Find the situation in the database
                situation_data = next((item for item in first_aid_database if item["situation"] == symptom), None)
                if situation_data:
                    solution = situation_data["solution"]
                    follow_up = situation_data.get("followUp", {})
                    follow_up_question = follow_up.get("question", None)
                    follow_up_answer = None

                    if answer == 'yes' and follow_up:
                        follow_up_answer = follow_up["answer"]["yes"]
                    elif answer == 'no' and follow_up:
                        follow_up_answer = follow_up["answer"]["no"]
                else:
                    solution = "No solution found. Please consult a professional."
                    follow_up_question = None
                    follow_up_answer = None

                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = json.dumps({
                    "solution": solution,
                    "followUpQuestion": follow_up_question,
                    "followUpAnswer": follow_up_answer
                })
                self.wfile.write(response.encode('utf-8'))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Invalid JSON')

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run() 