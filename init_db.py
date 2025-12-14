import sqlite3

conn = sqlite3.connect('db.sqlite')

with open('proj_schema.sql','r',encoding='utf-8')as f:
    schema = f.read()

conn.executescript(schema)
conn.commit()
conn.close()

print("DB생성완료:db.sqlite")