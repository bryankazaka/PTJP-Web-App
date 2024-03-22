from flask import Flask, render_template
from flask_sock import Sock
from flask_mysqldb import MySQL, MySQLdb
import TransportPlanner
import atexit

# PTJPApp Server. This program runs the server side of the PTJP App, communicating with the Application Layer to complete
# tasks specified by users (e.g. search, log in).
#
# Author      : Michael Schoots
# Last Updated: 28 September 2022


# Set up app, socket and database
app  = Flask(__name__)
sock = Sock(app)
app.secret_key = 'TEMP_SECRET_KEY'

# Define your database information **N.B. MUST BE DONE BY SERVER ADMIN**
host     = 'localhost'
user     = 'root'
password = '54265'
database = 'PTJPApp'

db = MySQL(app)

# Change the link you want the server to run on
link = '127.0.0.1'

# Lists of closed stations and lines
stations = []
lines    = []

# List of current active users
users    = []

# Define admin key (can be changed)
ADMIN_KEY = '54862'

# Generate Trainlines library and graph
TRAINLINES = TransportPlanner.dictFunction()
    
@app.before_request
def make_session_permanent():
    app.permanent = False

# Directs users upon connecting to the main view
@app.route('/')
def index():
    return render_template('main_view.html')

# Server side of a search
@sock.route('/searchSubmitted')
def searchSubmitted(sock):
    while True:
        # Read in data from user
        data   = sock.receive()
        search = data.split('/')

        # Split search submission into usable components
        username        = search[0]
        search_from     = search[1]
        search_to       = search[2]
        search_schedule = search[3]
        search_filter   = search[4]
        try:
            # test added to ensure input for time is valid
            test = TransportPlanner.str_to_time(search[5])
            search_time = search[5]
        except:
            search_time = ''

        # In the case where all inputs are not entered, notify user.
        if search_from=="Choose" or search_to=="Choose" or search_schedule=="Choose" or search_filter=="Choose" or search_time=="":
            sock.send("Not Complete")

        else:
            # Calculate shortest path 
            try:
                # Check the stations and lines array to see if there are any closed stations. Else, make input array usable for the algorithm
                if len(stations) > 0:
                    closed_stations = stations
                else:
                    closed_stations = ['']

                if len(lines) > 0:
                    closed_lines = lines
                else:
                    closed_lines = [''] 

                # Check for the case that both stations inputted are the same
                if search_from.upper() == search_to.upper():
                    sock.send('Same stations')

                # Check if entered stations are currently blocked
                if search_from.upper() in stations:
                    sock.send('Station blocked')

                elif search_to.upper() in stations:
                    sock.send('Station blocked')

                else:
                    # Calculate the route
                    route = TransportPlanner.getOutput_schedule(TRAINLINES, search_from.upper(), search_to.upper(), search_schedule, search_filter, search_time, closed_stations, closed_lines)
                    # In the case where one of the inputted 'stations' is not a station, notify user.
                    if str(route) == '-1':
                        sock.send('Invalid inputs')

                    # In the case where the algorithm is unable to produce a search
                    elif route == 'Sorry, something went wrong. Try another route!':
                        sock.send(route)

                    else:
                        # Check if there is any blockage in place, and add the necessary info to inform application layer.
                        if len(stations) > 0 or len(lines) > 0:
                            route = "Blockage#" + route
                        else:
                            route = "NoBlock#" + route

                        # Get the location of the route image
                        stations_list = ''
                        lines_list    = ''

                        if len(stations) > 0:
                            stations_list = stations[0]

                            for station in stations:
                                if station != stations[0]:
                                    stations_list += ',' + station

                        if len(lines) > 0:
                            lines_list = lines[0]

                            for line in lines:
                                if line != lines[0]:
                                    lines_list += ',' + line

                        image_location = str('../static/images/output_figure_' + search_from.upper() + '_' + search_to.upper() + '_' + stations_list + '_' + lines_list + '.jpeg')

                        # Add new search object to historical database if user logged in.
                        if username != 'none_logged_in':
                            mydb   = MySQLdb.connect(host=host, user=user, password=password, database=database)
                            cursor = mydb.cursor()
                            cursor.execute('INSERT INTO searches (username, search_from, search_to, search_schedule, search_filter, search_time, image, route) VALUES (% s, % s, % s, % s, % s, % s, % s, % s)', (username, search_from, search_to, search_schedule, search_filter, search_time, image_location, route, ))
                            mydb.commit()
                            cursor.close()
                            mydb.close()

                            # Get the id of the new stored search to send to Application layer.
                            mydb   = MySQLdb.connect(host=host, user=user, password=password, database=database)
                            cursor = mydb.cursor()
                            cursor.execute("SELECT id FROM searches WHERE username = % s ORDER BY id DESC LIMIT 1", (username, ))
                            temp = cursor.fetchone()
                            cursor.close()
                            mydb.close()
                            id = temp[0]

                        else:
                            id = 0
                        # Send route to the Application layer.
                        sock.send(str(id) + '///' + search_from + '///' + search_to + '///' + search_schedule + '///'  + search_filter + '///' + search_time + '///' + route + '///' + image_location)
            # Catch all in the case of an issue.
            except:
                sock.send('There was an issue with this journey. Please ensure both destinations are on the map.')

# Server side of logging in to the app.
@sock.route('/login')
def login(sock):
    while True:
        # Receive log in input from user.
        data = sock.receive()
        login_info = data.split('/')

        # Split login details into components.
        username = login_info[0]
        password = login_info[1]

        # Check database for this user.
        mydb   = MySQLdb.connect(host=host, user=user, password=password, database=database)
        cursor = mydb.cursor()
        #cursor = db.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = % s AND pwd = % s', (username, password, ))
        account = cursor.fetchone()
        cursor.close()
        mydb.close()
        #print(account)

        # If the account exists, notify application layer and send through previous searches (if any).
        if account:
            mydb   = MySQLdb.connect(host=host, user=user, password=password, database=database)
            cursor = mydb.cursor()
            cursor.execute("SELECT logged_in FROM users WHERE username = % s", (username, ))
            temp = cursor.fetchone()
            cursor.close()
            mydb.close()
            logged_in = temp[0]

            # Check if user is already logged in on another window. Only allow user to log in if they are not already logged in.
            if logged_in == "False":
                # Update database to show user is logged in.
                mydb   = MySQLdb.connect(host=host, user=user, password=password, database=database)
                cursor = mydb.cursor()
                cursor.execute('UPDATE users SET logged_in = "True" WHERE username = % s', (username, ))
                mydb.commit()
                cursor.close()
                mydb.close()

                # Add user to list of current users
                users.append(username)

                # Fetch all previous searches for the given user from the database.
                mydb   = MySQLdb.connect(host=host, user=user, password=password, database=database)
                cursor = mydb.cursor()
                cursor.execute('SELECT * FROM searches WHERE username = % s', (username, ))
                results = cursor.fetchall()
                cursor.close()
                mydb.close()
                sock.send('Successful login')

                # In the case where there are no previous searches, notify user.
                if len(results) == 0:
                    sock.send('No previous searches')
                # In the case where there are previous searches, send them each through to the application layer.
                else:
                    for row in results:
                        id              = row[0]
                        search_from     = row[2]
                        search_to       = row[3]
                        search_schedule = row[4]
                        search_filter   = row[5]
                        search_time     = row[6]
                        image           = row[7]
                        route           = row[8]

                        sock.send(str(id) + '///' + search_from + '///' + search_to + '///' + search_schedule + '///' + search_filter + '///' + search_time + '///' + route + '///' + image)
            # Case where user is already logged in, and so cannot be logged in in this window.
            else:
                sock.send('User is already logged in !')
        # Case where there is an issue with the inputted username or password.   
        else:
            sock.send('Incorrect username / password !')

# Server side of registering a new user - MJS
@sock.route('/register')
def register(sock):
    while True:
        # Recieve registration information from user.
        data = sock.receive()
        user = data.split('/')

        # Split the received information.
        username = user[0]
        password = user[1]

        # Check if the account already exists (username is unique).
        mydb   = MySQLdb.connect(host=host, user=user, password=password, database=database)
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
        account = cursor.fetchone()
        cursor.close()
        mydb.close()

        # If account already exists, notify user.
        if account:
            sock.send('Username already in use. Please choose a different one.')
        # Else, add user to database and inform user of successful registration.
        else:
            mydb   = MySQLdb.connect(host=host, user=user, password=password, database=database)
            cursor = mydb.cursor()
            cursor.execute('INSERT INTO users (username, pwd, logged_in) VALUES (% s, % s, "False")', (username, password, ))
            mydb.commit()
            cursor.close()
            mydb.close()
            sock.send('Successfully registered account. Username: ' + username + ' and Password: ' + password + '.')

# Server side of logging out of an account.
@sock.route('/logout')
def logout(sock):
    while True:
        # Receive user to be logged out from application layer.
        username = sock.receive() 
        print(username)

        # Update database to show the given user is logged out.
        mydb   = MySQLdb.connect(host=host, user=user, password=password, database=database)
        cursor = mydb.cursor()
        cursor.execute('UPDATE users SET logged_in = "False" WHERE username = % s', (username, ))
        mydb.commit()
        cursor.close()
        mydb.close()

        # Remove user from list of current users
        users.remove(username)

        # Inform application layer of this change.
        try:
            sock.send('User logged out')
        except:
            pass


# Server side of deleting a previous search.
@sock.route('/deleteSearch')
def deleteSearch(sock):
    while True:
        # Recieve the id of the search to be deleted from user.
        id = sock.receive()

        # Delete search from the database.
        mydb   = MySQLdb.connect(host=host, user=user, password=password, database=database)
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM searches WHERE id = % s", (id, ))
        mydb.commit()
        cursor.close()
        mydb.close()

        # Send back id so it can be deleted from previous searches table.
        sock.send(id)

# Route to initiate admin control.
@app.route('/admin')
def admin():
    return render_template('admin_view.html', stations=stations, lines=lines)

# Verify the admin code to allow access to admin functionality.
@sock.route('/verifyAdmin')
def verifyAdmin(sock):
    while True:
        # Receive input code from user.
        code = sock.receive()

        # If the code matches ADMIN_KEY, allow admin access.
        if code == ADMIN_KEY:
            sock.send('Correct Code')

            # Send through to admin control all stations currently closed.
            if len(stations) != 0:
                for station in stations:
                    sock.send("Station/" + station)
            else:
                sock.send("No Stations Closed")
            
            # Send through to admin control all lines currently closed.
            if len(lines) != 0:
                for line in lines:
                    sock.send("Line/" + line)
            else:
                sock.send("No Lines Closed")
        # In the case where the wrong code is inputted, notify user.
        else:
            sock.send('Wrong Code')

# Server side of admin functionality for opening up a currently closed station/line.
@sock.route('/open')
def open(sock):
    while True:
        # Receive the information from the application layer.
        data = sock.receive()
        temp = data.split('/')

        # Admin requests opening a station.
        if temp[0] == 'Station':
            stations.remove(temp[1])
            sock.send('Opened Station/' + temp[1])
        # Admin requests opening a line.
        else:
            lines.remove(temp[1])
            sock.send('Opened Line/' + temp[1])
        # NOTE: We do not need to validate that temp[1] is a station/line as the 'open' call on the application side
        # is tied directly to that station/line on creation of table row created when a station/line is closed.

# Server side of the admin functionality for closing a station/line.
@sock.route('/adminControl')
def adminControl(sock):
    while True:
        # Receive data from application layer.
        data = sock.receive()
        data = data.split("/")

        # Split return into usable parts.
        request = data[0]
        input   = data[1]

        # If the admin is requesting blocking a station.
        if request == "block_station":
            # Check is station is already blocked.
            inList = False
            for station in stations:
                if station == input.upper():
                    inList = True
                    break
            
            # If station is already block, notify admin.
            if inList:
                sock.send('Station is already blocked.')
            # If station is not currently blocked, add to the list of blocked stations.
            else:
                stations.append(input.upper())
                #print(stations)
                sock.send('Station blocked/' + input.upper())
  
        # If the admin is requesting blocking a train line.
        elif request == "block_line":
            # Check if line is already blocked.
            inList = False
            for line in lines:
                if line == input.upper():
                    inList = True
                    break
            
            # If line is already blocked, notify admin.
            if inList:
                sock.send('Train Line is already blocked')
            # If line is not blocked, add to the list of blocked lines.
            else:
                lines.append(input.upper())
                sock.send('Train Line blocked/' + input.upper())

# Function called when the server is closed to clean up
@atexit.register
def close_server():
    for user in users:
        mydb   = MySQLdb.connect(host=host, user=user, password=password, database=database)
        cursor = mydb.cursor()
        cursor.execute('UPDATE users SET logged_in = "False" WHERE username = % s', (user, ))
        mydb.commit()
        cursor.close()
        mydb.close()

if __name__ == "__main__":
    app.run(debug=False, host=link, port=5000)