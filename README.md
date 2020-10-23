# Movie Project for Balto

A simple CRUD app built with docker, flask, MySQL, and a lil Nginx.

## Running the app

make sure you have docker and docker compose installed.

From the project directory you can...

build the app:

`docker-compose build`

run the app:

`docker-compose up`

shut it down:

`docker-compose down`

## Using the app

A simple web page is exposed at http://localhost with several buttons for interaction.
This page is primarily designed for testing the flask api.

The app starts with a small sample of pre-loaded test data. If you want to load the
full movies csv provided, you can use the file uploader.

**Search** sends a query that returns movie entries with partial string matches

**Add Movie** adds a test movie with data hardcoded in index.html

**Update Movie** Does a partial update of an existing record with data hardcoded in index.html

**Delete Movie** Deletes an existing record based on id, also hardcoded in index.html

**Choose File** allows the user to upload new data in bulk from a .csv file.
WARNING: The large data file provided will take > 1 min to upload.


## Whats inside

`/app` a containerized flask api

`/db` configuration file for MySQL setup

`/web` a simple index.html served with Nginx, and a reverse-proxy for api requests


## Sources and references

[Google Doc](https://docs.google.com/document/d/1kINlgQfMGVam617ZXN-v2cTbeIljhVmdlhDjyqEoDbc/edit?usp=sharing)
