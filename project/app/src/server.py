
import os
from flask import Flask, jsonify, request
import json
import mysql.connector
import pandas as pd
from sqlalchemy import types, create_engine

server = Flask(__name__)
conn = None

class DBManager:
    def __init__(self, database='example', host="db", user="root", password_file='/run/secrets/db-password'):
        pf = open(password_file, 'r')
        self.DB_USER = user
        self.DB_PASS = pf.read()
        self.DB_HOST = host
        self.DB_DATABASE = database
        
        self.connection = mysql.connector.connect(
            user=self.DB_USER, 
            password=self.DB_PASS,
            host=self.DB_HOST,
            database=self.DB_DATABASE,
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
                    cast VARCHAR(255),
                    genre VARCHAR(255),
                    wiki_link VARCHAR(255),
                    plot TEXT)
                '''
        )

        # Insert some initial sample data
        sql= "INSERT INTO movie (release_year, title, origin, director, cast, genre, wiki_link, plot) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = [
            (1999, 'Titanic', 'American', 'Abraham Lincoln', 'the ninja turtles', 'action', 'www.wikipedia.com', 'A promising inventor accidentally splices thier DNA with a fly and turns into a monster'),
            (1989, 'Back to the Future', 'American', 'Teddy Roosevelt','the ninja turtles', 'Drama', 'www.wikipedia.com', 'The following plot synopsis was published in conjunction with a 1915 showing of the film at Carnegie Hall'),
            (1989, 'Back to the Future Pt. III', 'American', 'Franklin Roosevelt','the ninja turtles', 'Comedy', 'www.wikipedia.com', 'a 1915 showing of the film at Carnegie Hall')
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

    def add_movie(self, movie):
        sql = "INSERT INTO movie (release_year, title, origin, director, cast, genre, wiki_link, plot) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (movie['year'], movie['title'], movie['origin'], movie['director'], movie['cast'], movie['genre'], movie['wiki'], movie['plot'])
        self.cursor.execute(sql, val)
        self.connection.commit()

    def update_movie(self, movie_id, field, value):
        _valid_columns = frozenset(['release_year', 'title', 'origin', 'director', 'cast' 'genre', 'wiki_link', 'plot'])
        if field not in _valid_columns:
            raise Exception('Column not found')
            
        sql = "UPDATE movie SET {column_name} = %s WHERE id = %s".format(column_name=field)
        val = (value, movie_id)
        self.cursor.execute(sql, val)
        self.connection.commit()

    """
    FIX ME: tried identical syntax to update_movie about, but
    can't get %s to map to movie_id for some reason here. Using the bad way.
    """
    def delete_movie(self, movie_id):
        sql = "DELETE FROM movie WHERE id = {}".format(movie_id)
        self.cursor.execute(sql)
        self.connection.commit()

    def upload_csv(self, csv_file):
        chunksize = 1000
        df = pd.read_csv(csv_file)
        #~ df.rename(columns={
            #~ df.columns[0]: "release_year",
            #~ df.columns[1]: "title",
            #~ df.columns[2]: "origin",
            #~ df.columns[3]: "director",
            #~ df.columns[4]: "genre",
            #~ df.columns[5]: "wiki_page",
            #~ df.columns[6]: "plot"
                #~ }, inplace=True)
                            
        #~ columns = list(df.columns)

        df.fillna("None", inplace= True)

        """
        The better way to import our df to mysql, all at once.
        It's not recognizing the movie table, so instead I'm adding them
        one at a time.
        """
        #engine = create_engine('mysql+mysqlconnector://'+self.DB_USER+':'+self.DB_PASS+'@'+self.DB_HOST+'/'+self.DB_DATABASE, echo=False)
        #~ df.to_sql(name='movie', con=engine, index=False, if_exists='replace')

        for index, row in df.iterrows():
            print("ITERATING ON DF")
            print(str(row))
            print(tuple(row))
            sql = "INSERT INTO movie (release_year, title, origin, director, cast, genre, wiki_link, plot) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = tuple(row)
            self.cursor.execute(sql, val)
            self.connection.commit()
        


# Initialize DB
if not conn:
    conn = DBManager()
    conn.populate_db()


@server.route('/movies', methods=['GET'])
def all_movies():
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

@server.route('/movies', methods=['POST'])
def add_movie():
    data = request.get_json()
    if data:
        global conn
        if not conn:
            conn = DBManager()
        try:    
            conn.add_movie(data)
            return jsonify({"response": "Successfully Added Movie"})

        except Exception as e:
            return jsonify({"response": str(e)})
            

@server.route('/movies', methods=['PATCH'])
def update_movie():
    data = request.get_json()
    if data:
        global conn
        if not conn:
            conn = DBManager()

        try:
            for key, value in data.items():
                if key != 'movie_id':
                    conn.update_movie(data['movie_id'], key, value)
            return jsonify({"response": "Successfully Updated Movie #" + str(data['movie_id'])})

        except Exception as e:
            return jsonify({"response": str(e)})

@server.route('/movies', methods=['DELETE'])
def delete_movie():
    data = request.get_json()
    if data:
        global conn
        if not conn:
            conn = DBManager()
        try:
            conn.delete_movie(data['movie_id'])
            return jsonify({"response": "Successfully Deleted Movie #" + str(data['movie_id'])})
            
        except Exception as e:
            return jsonify({"response": str(e)})

@server.route('/upload', methods=['POST'])
def upload():
    print("UPLOAD CALLED:")
    print(str(request.files['file']))
    data_file = request.files['file'];
    if data_file:
        global conn
        if not conn:
            conn = DBManager()
        try:
            conn.upload_csv(data_file)
            return jsonify({"response": "Successfully uploaded data from file"})

        except Exception as e:
            return jsonify({"response": str(e)})
            

if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0', port=5000)

