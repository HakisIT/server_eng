from http.server import HTTPServer, BaseHTTPRequestHandler
from flask import Flask, Response, request, json, redirect, url_for, render_template, jsonify
from flask_restful import Api, Resource
import mysql.connector
from flask_cors import CORS
import random
import json
import hashlib


HOST = '192.168.199.45'
PORT = 8080

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


def selection_main(word_id):
    sql_select_query = """SELECT * FROM main WHERE id = %s"""
    mycursor.execute(sql_select_query, (word_id,))
    word1 = mycursor.fetchall()
    dct = {word1[0][0]:[word1[0][1], word1[0][2], word1[0][3], word1[0][4]]}
    return dct

def selection_id():
    mycursor = mydb.cursor()
    mycursor.execute('SELECT id FROM main')
    words = mycursor.fetchall()
    id_lst = []
    for i in words:
        id_lst.append(i[0])
    return id_lst


def select_acticle(word_id):
    sql_select_query = """SELECT * FROM german_articles WHERE id = %s"""
    mycursor.execute(sql_select_query, (word_id,))
    word1 = mycursor.fetchall()
    dct = {word1[0][0]:[word1[0][1], word1[0][2]]}
    return dct

def select_acticle_id():
    mycursor = mydb.cursor()
    mycursor.execute('SELECT id FROM german_articles')
    words = mycursor.fetchall()
    id_lst = []
    for i in words:
        id_lst.append(i[0])
    return id_lst

def selection_word():
    sql_select_query = "SELECT english FROM main"
    mycursor.execute(sql_select_query)
    words = mycursor.fetchall()
    wrd = []
    for i in words:
        wrd.append(i[0][:-1])
    return wrd

def user_info():
    sql_select_query = "SELECT * FROM user_info"
    mycursor.execute(sql_select_query)
    users = mycursor.fetchall()
    user_info = {}
    for i in users:
        user_info.update({i[0]:[i[1], i[2], i[3], i[4]]})
    return user_info


def users_list():
    sql_select_query = "SELECT user_name FROM user_info"
    mycursor.execute(sql_select_query)
    users = mycursor.fetchall()
    users_lst = []
    for i in users:
        users_lst.append(i[0])
    return users_lst

def user_actions_id_list():
    sql_select_query = """SELECT user_id FROM user_actions"""
    mycursor.execute(sql_select_query)
    id_user_actions = mycursor.fetchall()
    id_list = []
    for i in id_user_actions:
        id_list.append(i[0])
    return id_list

def lst_main_words():
    sql_select_query = """SELECT english, russian, czech, german FROM main"""
    mycursor.execute(sql_select_query)
    words = mycursor.fetchall()
    words_list = []
    for i in words:
        words_list.append(i[0])
        words_list.append(i[1])
        words_list.append(i[2])
        words_list.append(i[3])
        print(i[3])
    return words_list

def token_chech(rcv_data):
    for key, sublist in user_info().items():
        if rcv_data['token'] in sublist:
            return key
    return False
        
def users_and_hash_list():
    sql_select_query = "SELECT user_name, password FROM user_info"
    mycursor.execute(sql_select_query)
    users = mycursor.fetchall()
    users_and_hash_lst = {}
    for i in users:
        users_and_hash_lst.update({i[0]:i[1]})
    return users_and_hash_lst

def validate_word(data):
    # check is digit in data
    if any(char.isdigit() for char in data['english']) or any(char.isdigit() for char in data['russian']) or any(char.isdigit() for char in data['czech'] or any(char.isdigit() for char in data['german'])):
        print('number validate')
        return False

    if data['english'] == '' or data['russian'] == '' or data['czech'] == '' or data['german'] == '':
        print('empty validate')
        return False
    
    if data['english'] in lst_main_words() or data['russian'] in lst_main_words() or data['czech'] in lst_main_words() or data['german'] in lst_main_words():
        print('existing word')
        return False
    return True


def add_new_word(rcv_data):
    print('rcv_data:', rcv_data)
    if validate_word(rcv_data) == True and token_chech(rcv_data) != False:
        sql_insert_query = """INSERT INTO main (english, russian, czech, german) 
                                    VALUES (%s, %s, %s, %s)"""
        tuple1 = (rcv_data['english'], rcv_data['russian'], rcv_data['czech'], rcv_data['german'])
        mycursor.execute(sql_insert_query, tuple1)
        mydb.commit()

        sql_select_query = """SELECT id FROM main WHERE english = %s AND russian = %s AND czech = %s AND german = %s"""
        mycursor.execute(sql_select_query, (rcv_data['english'], rcv_data['russian'], rcv_data['czech'], rcv_data['german']))
        words_id = mycursor.fetchall()
        mydb.commit()

        correct_user_id = token_chech(rcv_data)
        mycursor.execute("INSERT INTO user_actions (action, date, user_id, add_id) VALUES (%s, NOW(), %s, %s)", ('add', correct_user_id, words_id[0][0]))
        mydb.commit()
        return True
    elif validate_word(rcv_data) == True and token_chech(rcv_data) != True:
        return {'autorization':'fail'}
    else:
        return False
    

def validate_key(rcv_data):
    for key, sublist in user_info().items():
        if rcv_data['user'] in sublist:
            if key in user_actions_id_list():
                mycursor.execute("INSERT INTO user_actions (action, date, user_id) VALUES (%s, NOW(), %s)", (f'add', key))
                mydb.commit()
    

def validate_registration(data):    
    if data['user'] == '' or data['password'] == '' or data['email'] == '':
        return 'Fill in all the blanks'
    else:
        return True

def validate_autoriz(data):    
    if data['user'] == '' or data['password'] == '':
        return 'Fill in all the blanks'
    else:
        return True
    

def user_verification(user, password):
    if user in users_and_hash_list():
        if users_and_hash_list()[user] == hash_password(password):
            return True
        else:
            return False


def create_uuid():
    import uuid
    uuid_result = str(uuid.uuid1(random.randint(10, 10 ** 12)))
    return uuid_result


def hash_password(data):
    data_json = json.dumps(data)
    return hashlib.sha256(data_json.encode('utf-8')).hexdigest()


def add_new_user(rcv_data):
    print('add_new_user')
    if hash_password(rcv_data) != '' and validate_registration(rcv_data) == True and rcv_data['user'] not in users_list():
        hash_pass = hash_password(rcv_data['password'])
        sql_insert_query = """INSERT INTO user_info (user_name, password, email, uuid) 
                                    VALUES (%s, %s, %s, %s)"""
        tuple1 = (rcv_data['user'], hash_pass, rcv_data['email'], create_uuid())
        mycursor.execute(sql_insert_query, tuple1)
        mydb.commit()
        return True
    
    elif validate_registration(rcv_data) == 'Fill in all the blanks':
        return 'Fill in all the blanks'
    else:
        return False


def login(rcv_data):
    if validate_autoriz(rcv_data) == True and user_verification(rcv_data['user'], rcv_data['password']) == True:      
        return True
    
    elif validate_autoriz(rcv_data) == True and user_verification(rcv_data['user'], rcv_data['password']) == False:
        return 'Wrong password'
    elif validate_autoriz(rcv_data) == 'Fill in all the blanks':
        return 'Fill in all the blanks'
    else:
        return False
    

def add_uuid(rcv_data):
    for key, sublist in user_info().items():
        if rcv_data['user'] in sublist:
            if key in user_actions_id_list():
                mycursor.execute("INSERT INTO user_actions (action, date, user_id) VALUES (%s, NOW(), %s)", ('authorization', key))
                mydb.commit()
                print('add_uuid')
                uuid = create_uuid()
                mycursor.execute("UPDATE user_info SET uuid = %s WHERE id = %s", (uuid, key,))
                mydb.commit()
            else:
                sql_insert_query1 = """INSERT INTO user_actions (user_id, action)
                                        VALUES (%s, %s)"""
                tuple2 = (key, 'autorization')
                try:
                    mycursor.execute(sql_insert_query1, tuple2)
                    mydb.commit()
                except mysql.connector.IntegrityError as e:
                    print("Ошибка целостности:", e)
                    # Обработка ошибки дублирования записи здесь, если необходимо
    return uuid

def flash_card_translate(rcv_data, rnd_word):
    if rcv_data['lang'] == 'eng':
        return rnd_word[0]
    
    if rcv_data['lang'] == 'rus':
        return rnd_word[1]
    
    if rcv_data['lang'] == 'cz':
        return rnd_word[2]
    
    if rcv_data['lang'] == 'ger':
        print(rcv_data['lang'])
        return rnd_word[3]
    
    

@app.route('/search/<word>')
def search_text(word):
    if word in selection_word():
        return {'data': 'success'}
    else:
        return 'page not found, all posible id {}'.format(selection_id())
    

@app.route('/id/<int:word_id>')
def get(word_id):
    return selection_main(word_id)


@app.route('/add', methods=['POST'])
def process_data():
    if request.method=='POST':
        if request.data:
            rcv_data = json.loads(request.data.decode(encoding='utf-8'))

            if add_new_word(rcv_data) == True:
                return jsonify({'data': 'success'})
            elif add_new_word(rcv_data) == {'autorization':'fail'}:
                return jsonify({'data':'autorization before add new words'})
            else:
                return jsonify({'data': 'strings must not contain numbers and cannot be empty'})
        
@app.route('/random')
def random_id():
    rnd_id = random.choice(selection_id())
    return selection_main(rnd_id)
    
def random_words():
    random_word = list(random_id().values())[0]
    return random_word

def random_article_id():
    rnd_art_id = random.choice(select_acticle_id())
    return select_acticle(rnd_art_id)

def random_article():
    rnd_article = list(random_article_id().values())[0]
    return rnd_article
print(random_article())

@app.route('/translate', methods=['POST'])
def flash_card():
    if request.method == 'POST':
        if request.data:
            rcv_data = json.loads(request.data.decode(encoding='utf-8'))
            word = random_words()  # Получаем случайное слово
            print(word)
            resp = flash_card_translate(rcv_data, word)
            result = jsonify({'data': resp})
            return result

session_passed_word_count = 0
@app.route('/next', methods=['POST'])
def next_word():
    global session_passed_word_count
    if request.data:
        rcv_data = json.loads(request.data.decode(encoding='utf-8'))
        token = rcv_data['token']

        sql_select_query_2 = """
        SELECT passed_word_count
        FROM user_info 
        WHERE uuid = %s"""
        mycursor.execute(sql_select_query_2, (token, ))
        fetch = mycursor.fetchall()

        plus_1 = fetch[0][0]+1
        sql_insert_query = """
        UPDATE user_info
        SET passed_word_count = %s
        WHERE uuid = %s"""
        mycursor.execute(sql_insert_query, (plus_1, token))
        mydb.commit()

        word = random_words()  # Получаем случайное слово
        session_passed_word_count += 1     
        return jsonify({'data': word})        

            
            

@app.route('/registration', methods=['POST'])
def regist():
    global session_passed_word_count
    if request.data:
        rcv_data = json.loads(request.data.decode(encoding='utf-8'))
        session_passed_word_count = 0
        print('POST rcv_data', rcv_data)

        if add_new_user(rcv_data) == True:
            data = {'result_label':'Success authorization !'}
            return json.dumps(data)
        
        elif add_new_user(rcv_data) == 'Fill in all the blanks':
            data = {'result_label':'Fill in all the blanks'}
            return json.dumps(data)
        
        else:
            data = {'result_label':'This user already exists'}
            return json.dumps(data)
            
@app.route('/authorization', methods=['POST'])
def autoriz():
    global session_passed_word_count
    if request.data:
        rcv_data = json.loads(request.data.decode(encoding='utf-8'))
        print(request.data)
        session_passed_word_count = 0
        if login(rcv_data) == True:
            token = add_uuid(rcv_data)
            
            data = {'result_label':'Success authorization !', 'token': token}
            print(data)
            return json.dumps(data)
        
        elif login(rcv_data) == 'Wrong password':
            data = {'result_label':'Wrong password'}
            return json.dumps(data)
        
        elif login(rcv_data) == 'Fill in all the blanks':
            data = {'result_label':'Fill in all the blanks'}
            return json.dumps(data)
        
        else:
            data = {'result_label':'This user does not exist'}
            return json.dumps(data)

@app.route('/statistic', methods=['POST'])
def statist():
    if request.data:
        rcv_data = json.loads(request.data.decode(encoding='utf-8'))
        token = rcv_data['token']
        sql_select_query_1 = """
        SELECT user_id, action, add_id, uuid, english, russian, czech, german
        FROM user_actions 
        INNER JOIN user_info ON user_actions.user_id = user_info.id
        INNER JOIN main ON user_actions.add_id = main.id
        WHERE action = 'add' AND uuid = %s"""
        mycursor.execute(sql_select_query_1, (token, ))
        fetch_session = mycursor.fetchall()

        sql_select_query_2 = """
        SELECT passed_word_count
        FROM user_info 
        WHERE uuid = %s"""
        mycursor.execute(sql_select_query_2, (token, ))
        fetch = mycursor.fetchall()

        eng_words_list = []
        for i in fetch_session:
            eng_words_list.append(i[4])
        return {'pass_words':fetch[0][0],'session_pass_words': session_passed_word_count, 'add_words':eng_words_list}


# @app.route('/<usr>')
# def user(usr):
#     return f"<h1>{'Success add '+ usr}</h1>"




if __name__ == '__main__':
    app.run(debug=True, port=8080, host="192.168.199.45")