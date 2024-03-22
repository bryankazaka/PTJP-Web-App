# PTJPApp
The PTJPApp runs a search algorithm to find the shortest distance between two train stations
and returns it to a user.

# Installation
Open your terminal and navigate into PTJP Web App

Ensure the virtual environment is installed:
1. pip3 install virtualenv
2. virtualenv env
3. source env/bin/activate

When in the virtual environment, ensure the following are installed:
- All can be installed with pip3 install <name>
1. flask
2. flask-sock
3. matplotlib
4. networkx

Ensure MySQL is installed.
- Documentation to download MySQL:
    https://dev.mysql.com/downloads/installer/

5. Install flask-mysqldb
    - sudo apt-get install libmysqlclient-dev
    - pip3 install flask_mysqldb

6. Open MySQL Workbench and open a MySQL Server
7. Open PTJPAppDatabase.sql in the server and run to create database

# Usage
1. Check that PTJPApp database has been created 
2. Open PTJPApp.py and update 'host', 'user', and 'password' where it says 'define your database information' (ln 19)
    to match the specifics of your MySQL server
3. Open your terminal
4. Activate your virtualenv
    source env/bin/activate
5. Run PTJPApp.py
    python PTJPApp.py

