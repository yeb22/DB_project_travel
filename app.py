from flask import Flask, render_template
import sqlite3

app=Flask(__name__)

@app.route('/')
@app.route('/users/')
def showUsers():
    db=sqlite3.connect('db.sqlite')
    db.row_factory = sqlite3.Row

    cursor = db.cursor()

    users=cursor.execute(
        'SELECT uID, uName, preference FROM Users'
    ).fetchall()

    db.close()
    return render_template('users.html',users=users)

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1',port=5000)