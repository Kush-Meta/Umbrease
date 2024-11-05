from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = '123!123'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Your MySQL username
app.config['MYSQL_PASSWORD'] = 'flash788'  # Your MySQL password
app.config['MYSQL_DB'] = 'umbrease'

mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        account = cursor.fetchone()

        if account:
            # Store user_id in session
            session['user_id'] = account['id']
            return redirect(url_for('dashboard'))
        else:
            flash("Login failed. Please check your credentials.")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username ends with '@emory.edu'
        if not username.endswith('@emory.edu'):
            flash('Username must end with @emory.edu!')
            return redirect(url_for('signup'))

        # Validate format: Ensure the username is alphanumeric before @emory.edu
        if not re.match(r'^[a-zA-Z0-9._%+-]+@emory\.edu$', username):
            flash('Invalid username format! Please use a valid Emory email.')
            return redirect(url_for('signup'))

        # Check if the username already exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        account = cursor.fetchone()

        if account:
            flash('A user with this email already exists!')
            return redirect(url_for('signup'))
        else:
            # Insert new user into the database
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            mysql.connection.commit()
            flash('You have successfully registered! Please log in.')
            return redirect(url_for('login'))  # Redirect to login page

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'user_id' in session:
        user_id = session['user_id']
        
        # Get the user's details
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        # Fetch the number of available umbrellas
        cursor.execute("SELECT COUNT(*) AS available_umbrellas FROM umbrellas WHERE status = 'available'")
        umbrella_data = cursor.fetchone()
        
        # Fetch the user's rental history
        cursor.execute("SELECT umbrella_id, rental_date, return_date FROM rentals WHERE user_id = %s", (user_id,))
        rental_history = cursor.fetchall()

        # Pass data to the template
        return render_template('dashboard.html', 
                               username=user['username'],
                               available_umbrellas=umbrella_data['available_umbrellas'],
                               rental_history=rental_history)
    else:
        # If the user is not logged in, redirect to login page
        return redirect(url_for('login'))
    
@app.route('/rent_umbrella', methods=['POST'])
def rent_umbrella():
    if 'user_id' in session:
        user_id = session['user_id']
        
        # Find the first available umbrella
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id, code FROM umbrellas WHERE status = 'available' LIMIT 1")
        umbrella = cursor.fetchone()
        
        if umbrella:
            umbrella_id = umbrella['id']
            umbrella_code = umbrella['code']
            rental_date = datetime.now()
            due_date = rental_date + timedelta(hours=24)  # 24 hours later, for reference only

            # Insert into rentals table with due_date as a reference
            cursor.execute("""
                INSERT INTO rentals (user_id, umbrella_id, rental_date, return_date)
                VALUES (%s, %s, %s, NULL)
            """, (user_id, umbrella_id, rental_date))

            # Update the umbrella status to rented
            cursor.execute("UPDATE umbrellas SET status = 'rented' WHERE id = %s", (umbrella_id,))
            mysql.connection.commit()

            # Return a JSON response with the rental information
            return jsonify({
                "success": True,
                "message": f"Umbrella {umbrella_code} rented successfully! Please return within 24 hours.",
                "rental_date": rental_date.strftime("%Y-%m-%d %H:%M:%S"),
                "due_date": due_date.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        else:
            return jsonify({"success": False, "message": "No umbrellas available at the moment."})
    else:
        return jsonify({"success": False, "message": "Please log in to rent an umbrella."})
    
@app.route('/return_umbrella', methods=['POST'])
def return_umbrella():
    if 'user_id' in session:
        user_id = session['user_id']
        
        # Find the user's currently rented umbrella (one with a NULL return_date)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT umbrella_id FROM rentals 
            WHERE user_id = %s AND return_date IS NULL
            ORDER BY rental_date DESC LIMIT 1
        """, (user_id,))
        rental = cursor.fetchone()
        
        if rental:
            umbrella_id = rental['umbrella_id']
            return_time = datetime.now()
            
            # Update the rentals table to set the return date
            cursor.execute("UPDATE rentals SET return_date = %s WHERE user_id = %s AND umbrella_id = %s AND return_date IS NULL",
                           (return_time, user_id, umbrella_id))

            # Update the umbrella status to available
            cursor.execute("UPDATE umbrellas SET status = 'available' WHERE id = %s", (umbrella_id,))
            mysql.connection.commit()
            
            # Return a JSON response indicating success
            return jsonify({"success": True, "message": "Umbrella returned successfully and is now available for rent!"})
        else:
            # No currently rented umbrella found for this user
            return jsonify({"success": False, "message": "You have no umbrella to return."})
    else:
        # User is not logged in
        return jsonify({"success": False, "message": "Please log in to return an umbrella."})

    
if __name__ == '__main__':
    app.run(debug=True)
