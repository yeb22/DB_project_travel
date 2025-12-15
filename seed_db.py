import sqlite3
DB_NAME = 'db_sqlite'

conn= sqlite3.connect(DB_NAME)

with open("sql/seed_destinations.sql","r",encoding="utf-8") as f:
    seed_sql=f.read()
conn.executescript(seed_sql)
conn.commit()
conn.close()

print("Seed data inserted into db.sqlite")