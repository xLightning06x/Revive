import json
from http.server import BaseHTTPRequestHandler, HTTPServer

# Dummy database of symptoms and solutions
first_aid_database = {
    "bleeding": "Apply pressure to the wound and elevate the injured area.",
    "burn": "Cool the burn under running water for at least 10 minutes.",
    "choking": "Perform the Heimlich maneuver if the person is conscious.",
    # Add more symptoms and solutions as needed
}

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/first-aid.html'
        try:
            # Serve the HTML file
            with open(self.path[1:], 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File not found')

    def do_POST(self):
        if self.path == '/first-aid':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            symptoms = data.get('symptoms', '').lower()

            # Simple AI logic to find a solution
            solution = first_aid_database.get(symptoms, "No solution found. Please consult a professional.")

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"solution": solution})
            self.wfile.write(response.encode('utf-8'))

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run() 