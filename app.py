from flask import Flask, render_template,request, redirect, url_for
import sqlite3

app = Flask(__name__, template_folder="templates")

#user
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

#group
@app.route('/groups/')
def showGroups():
    db = sqlite3.connect('db.sqlite')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    groups = cursor.execute(
        'SELECT gID, gName, budget, cnt_members FROM Groups'
    ).fetchall()

    db.close()
    return render_template('groups.html', groups=groups)

@app.route('/groups/new/')
def newGroup():
    return render_template('groups_new.html')

@app.route('/groups/create/', methods=['POST'])
def createGroup():
    gname=request.form['gName']
    budget=request.form['budget']
    cnt=request.form['cnt_members']

    db = sqlite3.connect('db.sqlite')
    cursor = db.cursor()

    cursor.execute(
        'INSERT INTO Groups (gName, budget, cnt_members) VALUES (?, ?, ?)',
        (gname, budget, cnt)
    )

    db.commit()
    db.close()
    return redirect(url_for('showGroups'))

#group members

@app.route('/group_members/')
def showGroupMembers():
    db = sqlite3.connect('db.sqlite')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    rows = cursor.execute("""
        SELECT gm.gmID, g.gName, u.uName
        FROM Group_members gm
        JOIN Groups g ON gm.gID = g.gID
        JOIN Users u ON gm.uID = u.uID
        ORDER BY gm.gmID DESC
    """).fetchall()

    db.close()
    return render_template('group_members.html', rows=rows)

@app.route('/group_members/new/')
def newGroupMember():
    db = sqlite3.connect('db.sqlite')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    groups = cursor.execute("SELECT gID, gName FROM Groups ORDER BY gID DESC").fetchall()
    users = cursor.execute("SELECT uID, uName FROM Users ORDER BY uID DESC").fetchall()

    db.close()
    return render_template('group_members_new.html', groups=groups, users=users)

@app.route('/group_members/create/', methods=['POST'])
def createGroupMember():
    gID = request.form['gID']
    uID = request.form['uID']

    db = sqlite3.connect('db.sqlite')
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO Group_members (gID, uID) VALUES (?, ?)",
        (gID, uID)
    )

    db.commit()
    db.close()
    return redirect(url_for('showGroupMembers'))

#date
@app.route('/dates/')
def showDates():
    db = sqlite3.connect('db.sqlite')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    rows = cursor.execute("""
        SELECT d.dateID, u.uName, d.date
        FROM UDate d
        JOIN Users u ON d.uID = u.uID
        ORDER BY d.date
    """).fetchall()

    db.close()
    return render_template('dates.html', rows=rows)

@app.route('/dates/new/')
def newDate():
    db = sqlite3.connect('db.sqlite')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    users = cursor.execute(
        "SELECT uID, uName FROM Users ORDER BY uID"
    ).fetchall()

    db.close()
    return render_template('dates_new.html', users=users)

@app.route('/dates/create/', methods=['POST'])
def createDate():
    uID = request.form['uID']
    date = request.form['date']

    db = sqlite3.connect('db.sqlite')
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO UDate (uID, date) VALUES (?, ?)",
        (uID, date)
    )

    db.commit()
    db.close()
    return redirect(url_for('showDates'))

#commom dates
@app.route('/groups/<int:gID>/common_dates/')
def commonDates(gID):
    db = sqlite3.connect('db.sqlite')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    group = cursor.execute(
        "SELECT gName FROM Groups WHERE gID = ?",
        (gID,)
    ).fetchone()

    with open('sql/common_dates.sql', 'r', encoding='utf-8') as f:
        sql = f.read()

    common_dates = cursor.execute(sql, (gID, gID)).fetchall()
    db.close()

    return render_template(
        'common_dates.html',
        group=group,
        gID=gID,
        common_dates=common_dates
    )

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1',port=5000)