#!/bin/bash
 #
 ## Run script to create database
 python3 create_sql_db_using_python.py
 #

 sleep 10
 ## Run the Flask application

 python3 app.py --host=0.0.0.0 --port=8080
 exec "$@"