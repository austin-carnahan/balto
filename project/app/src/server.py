
import os
import flask
import json
import mysql.connector

# for debugging from Visual Studio Code -- turn off flask debugger first
# import ptvsd
# ptvsd.enable_attach(address=('0.0.0.0', 3000))

class DBManager:
    def __init__(self, database='example', host="db", user="root", password_file='/run/secrets/db-password'):
        pf = open(password_file, 'r')
        self.connection = mysql.connector.connect(
            user=user, 
            password=pf.read(),
            host=host,
            database=database,
            auth_plugin='mysql_native_password'
        )
        pf.close()
        self.cursor = self.connection.cursor()

    def populate_db(self):
        self.cursor.execute('DROP TABLE IF EXISTS movie')
        self.cursor.execute("CREATE TABLE movie (id INT AUTO_INCREMENT NOT NULL PRIMARY KEY, release_year INT, title VARCHAR(255), origin VARCHAR(255), director VARCHAR(255), genre VARCHAR(255), wiki_link VARCHAR(255), plot TEXT)")
        sql= "INSERT INTO movie (release_year, title, origin, director, genre, wiki_link, plot) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = [
            (1999, 'Titanic', 'American', 'Abraham Lincoln', 'action', 'www.wikipedia.com', 'A promising inventor accidentally splices thier DNA with a fly and turns into a monster'),
            (1989, 'Back to the Future', 'American', 'Teddy Roosevelt', 'Drama', 'www.wikipedia.com', 'The following plot synopsis was published in conjunction with a 1915 showing of the film at Carnegie Hall')
        ]
        
        self.cursor.executemany(sql, val)
        self.connection.commit()
    
    def query_titles(self):
        self.cursor.execute('SELECT title FROM movie')
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec


server = flask.Flask(__name__)
conn = None

# Initialize DB
if not conn:
    conn = DBManager()
    conn.populate_db()
    conn.connection.close()
    conn = None

@server.route('/blogs')
def listBlog():
    global conn
    if not conn:
        conn = DBManager()
        conn.populate_db()
    rec = conn.query_titles()

    result = []
    for c in rec:
        result.append(c)

    return flask.jsonify({"response": result})

@server.route('/')
def hello():
    global conn
    if not conn:
        conn = DBManager(password_file='/run/secrets/db-password')
        #~ conn.populate_db()
    rec = conn.query_titles()

    result = []
    for c in rec:
        result.append(c)

    return flask.jsonify({"response": result, "test": "test string"})
    #~ return flask.jsonify({"response": "Hello from Docker!"})


if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0', port=5000)

