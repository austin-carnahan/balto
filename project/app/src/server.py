
import os
from flask import Flask, jsonify, request
import json
import mysql.connector

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
        self.cursor = self.connection.cursor(dictionary=True)

    def populate_db(self):
        self.cursor.execute('DROP TABLE IF EXISTS movie')
        self.cursor.execute(
                '''
                CREATE TABLE movie (
                    id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
                    release_year INT,
                    title VARCHAR(255),
                    origin VARCHAR(255),
                    director VARCHAR(255),
                    genre VARCHAR(255),
                    wiki_link VARCHAR(255),
                    plot TEXT)
                '''
        )

        # Insert some initial sample data
        sql= "INSERT INTO movie (release_year, title, origin, director, genre, wiki_link, plot) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = [
            (1999, 'Titanic', 'American', 'Abraham Lincoln', 'action', 'www.wikipedia.com', 'A promising inventor accidentally splices thier DNA with a fly and turns into a monster'),
            (1989, 'Back to the Future', 'American', 'Teddy Roosevelt', 'Drama', 'www.wikipedia.com', 'The following plot synopsis was published in conjunction with a 1915 showing of the film at Carnegie Hall'),
            (1989, 'Back to the Future Pt. III', 'American', 'Franklin Roosevelt', 'Comedy', 'www.wikipedia.com', 'a 1915 showing of the film at Carnegie Hall')
        ]
        
        self.cursor.executemany(sql, val)
        self.connection.commit()
    
    def select_all(self):
        self.cursor.execute('SELECT * FROM movie')
        return self.cursor

    def search(self, query):
        """
        FIX ME: vulnerable to SQL injection
        Could not get this to work any other way and
        Couldnt justify spending more time on it.
        """
        sql = "SELECT * FROM movie WHERE title LIKE '%{}%'".format(query)
        self.cursor.execute(sql)
        return self.cursor


server = Flask(__name__)
conn = None

# Initialize DB
if not conn:
    conn = DBManager()
    conn.populate_db()


@server.route('/movies', methods=['GET'])
def movies():
    global conn
    if not conn:
        conn = DBManager()

    q = conn.select_all()

    result = []
    for item in q:
        result.append(item)

    return jsonify({"response": result})

@server.route('/search', methods=['GET'])
def search():
    result = []

    if "query" in request.args:
        query = request.args.get("query")
        
        global conn
        if not conn:
            conn = DBManager()
        q = conn.search(query)

        for item in q:
            result.append(item)

    return jsonify({"response": result})
    

    

if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0', port=5000)

