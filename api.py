from http.server import HTTPServer, BaseHTTPRequestHandler
from flask import Flask, Response, request, jsonify
from flask_restful import Api, Resource
import mysql.connector
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)
api = Api()

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='12312q',
    port='3306',
    database='english_words',
)
mycursor = mydb.cursor()



def selection_id(word_id):
    sql_select_query = """SELECT * FROM main WHERE id = %s"""
    mycursor.execute(sql_select_query, (word_id,))
    word1 = mycursor.fetchall()
    dct = {word1[0][0]:[word1[0][1], word1[0][2], word1[0][3]]}
    return Response(str(dct), content_type='text/html; charset=utf-8')

def selection_word():
    sql_select_query = "SELECT english FROM main"
    mycursor.execute(sql_select_query)
    words = mycursor.fetchall()
    wrd = []
    for i in words:
        wrd.append(i[0][:-1])
    return wrd

# class Main(Resource):
#     def get(self, word_id):
#         return selection_id(word_id)

@app.route('/search/<word>')
def search_text(word):
    if word in selection_word():
        return {'data': 'success'}
    else:
        return 'page not found'
    

@app.route('/words/<int:word_id>')
def get(word_id):
    return selection_id(word_id)

@app.route('/add', methods=['POST'])
def process_data():
    # Получаем данные из POST-запроса
    data = request.json()

    # Обрабатываем полученные данные
    english = data.get('english')
    russian = data.get('russian')
    czech = data.get('czech')

    # Возвращаем результат в виде JSON
    return jsonify({
        'english': english,
        'russian': russian,
        'czech': czech
    })


# url = 'http://192.168.1.35:9999/add'
data1 = {
    'english': '123',
    'russian': '456',
    'czech': '789'
}
response = requests.post('http://192.168.1.35:9999/add', data=data1)

print(response.text)

# api.add_resource(Main, '/words/<int:word_id>')
# api.init_app(app)

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
