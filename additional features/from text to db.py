#This algorithm imports each line of an "article-word-translation" format file (Die Zeit - Time) into the database

import mysql.connector
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='12312q',
    port='3306',
    database='english_words',
)
mycursor = mydb.cursor()

file = open("C:/Users/Yaroslav/Documents/test/de.txt", "r", encoding="utf8")

for i in file:
    new_string = i[:-1]
    separated_string = new_string.split(' ')
    final_dict = {separated_string[0]:[separated_string[1], separated_string[3]]}
    print(final_dict)
    mycursor.execute("INSERT INTO german_articles (article, word, translation) VALUES (%s, %s, %s)", (list(final_dict.keys())[0], list(final_dict.values())[0][0], list(final_dict.values())[0][1]))
    mydb.commit()