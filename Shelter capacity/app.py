# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
app = Flask(__name__)
# Create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('shelter.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create the database table (run this once or check if it exists)
def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS shelters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shelter_name TEXT NOT NULL,
            current_capacity INTEGER NOT NULL,
            max_capacity INTEGER NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

# Route to display the form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        shelter_name = request.form['shelterName']
        current_capacity = request.form['currentCapacity']
        max_capacity = request.form['maxCapacity']
        # Store data in the SQLite database
        conn = get_db_connection()
        conn.execute('INSERT INTO shelters (shelter_name, current_capacity, max_capacity) VALUES (?, ?, ?)',
                     (shelter_name, current_capacity, max_capacity))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

if __name__ == '__main__':
    create_table()  # Ensure the table is created
    app.run(debug=True)
