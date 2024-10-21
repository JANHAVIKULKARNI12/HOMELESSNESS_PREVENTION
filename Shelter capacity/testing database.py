import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('shelter.db')

# Retrieve all shelter data
shelters = conn.execute('SELECT * FROM shelters').fetchall()

# Print the data
for shelter in shelters:
    print(dict(shelter))

conn.close()
