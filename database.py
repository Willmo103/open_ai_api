import os, sqlite3

conn = sqlite3.connect("globals.db")

cursor = conn.cursor()

cursor.execute("""
               CREATE TABLE""")
