from http.server import HTTPServer, BaseHTTPRequestHandler
from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api()


users = {
    1: {'Jhon': 30},
    2: {'Mike':20}
}


class Main(Resource):
    def get(self, user_id):
        if user_id == 0:
            return users
        else:
            return users[user_id]


api.add_resource(Main, '/api/users/<int:user_id>')
api.init_app(app)





HOST = '192.168.1.35'
PORT = 9999


# class NeuralHTTP(BaseHTTPRequestHandler):
#     def do_GET(self):
#         self.send_response(200)
#         self.send_header('Content-type', 'text/html')
#         self.end_headers()
#         self.wfile.write(bytes("{'eng':'123'}", "utf-8"))



# server = HTTPServer((HOST, PORT), NeuralHTTP)
# responce = requests.get('http://192.168.1.35:9999/')
# fox = responce.json()
# print(fox)
# server.serve_forever()
# server.server_close()


if __name__ == '__main__':
    app.run(debug=True, port=9999, host="192.168.1.35")
