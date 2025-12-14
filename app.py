from flask import Flask, render_template,request, redirect, url_for
import sqlite3

app = Flask(__name__, template_folder="templates")

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

@app.route('/users/new/')
def newUser():
    return render_template('users_new.html')

@app.route('/users/create/',methods=['POST'])
def createUser():
    name = request.form['uName']
    pref = request.form['preference']

    db = sqlite3.connect('db.sqlite')
    cursor = db.cursor()

    cursor.execute(
        'INSERT INTO Users (uName, preference) VALUES (?,?)',(name, pref)

    )
    db.commit()
    db.close()
    return redirect(url_for('showUsers'))

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1',port=5000)