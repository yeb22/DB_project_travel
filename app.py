from flask import Flask, render_template,request, redirect, url_for
import sqlite3


app = Flask(__name__, template_folder="templates")

#user
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
    return redirect(url_for('index'))

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
    return redirect(url_for('index'))


#group members

@app.route('/group_members/')
def showGroupMembers():
    db = sqlite3.connect('db.sqlite')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    rows = cursor.execute("""
        SELECT gm.gmID, g.gName, u.uName
        FROM Group_members gm, Groups g, Users u
        WHERE gm.gID = g.gID
        AND gm.uID = u.uID
        ORDER BY gm.gmID DESC;
    """).fetchall()

    db.close()
    return render_template('group_members.html', rows=rows)

@app.route('/group_members/new/')
def newGroupMember():
    gID = request.args.get("gID")

    db = sqlite3.connect('db.sqlite')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    groups = cursor.execute("SELECT gID, gName FROM Groups ORDER BY gID DESC").fetchall()
    users = cursor.execute("SELECT uID, uName FROM Users ORDER BY uID DESC").fetchall()

    selected_group = None
    if gID:
        selected_group = cursor.execute(
            "SELECT gID, gName FROM Groups WHERE gID = ?",
            (gID,)
        ).fetchone()

    db.close()
    return render_template(
        'group_members_new.html',
        groups=groups,
        users=users,
        gID=gID,
        selected_group=selected_group
    )


@app.route('/group_members/create/', methods=['POST'])
def createGroupMember():
    gID = request.form['gID']
    uID = request.form['uID']
    next_url = request.form.get("next")

    db = sqlite3.connect('db.sqlite')
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO Group_members (gID, uID) VALUES (?, ?)",
        (gID, uID)
    )

    db.commit()
    db.close()
    if next_url:
        return redirect(next_url)
    return redirect(url_for('showGroupMembers'))

#date
@app.route('/dates/')
def showDates():
    db = sqlite3.connect('db.sqlite')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    rows = cursor.execute("""
        SELECT d.dateID, u.uName, d.date
        FROM UDate d, Users u
        WHERE d.uID = u.uID
        ORDER BY d.date;
    """).fetchall()

    db.close()
    return render_template('dates.html', rows=rows)

@app.route('/dates/new/')
def newDate():
    gID = request.args.get("gID")

    db = sqlite3.connect('db.sqlite')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    if gID:
        users = cursor.execute("""
        SELECT uID, uName
        FROM Users
        WHERE uID IN (
            SELECT uID
            FROM Group_members
            WHERE gID = ?
        )
        ORDER BY uName;
        """, (gID,)).fetchall()
    else:
        users = cursor.execute(
            "SELECT uID, uName FROM Users ORDER BY uID"
        ).fetchall()

    db.close()
    return render_template('dates_new.html', users=users, gID=gID)

@app.route('/dates/create/', methods=['POST'])
def createDate():
    uID = request.form['uID']
    date = request.form['date']

    next_url = request.form.get("next_url")

    db = sqlite3.connect('db.sqlite')
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO UDate (uID, date) VALUES (?, ?)",
        (uID, date)
    )

    db.commit()
    db.close()
    if next_url:
        return redirect(next_url)
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
#recommendation
@app.route("/groups/<int:gID>/recommend/")
def recommendByGroup(gID):
    db = sqlite3.connect("db.sqlite")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    group = cursor.execute(
        "SELECT gID, gName, budget FROM Groups WHERE gID = ?",
        (gID,)
    ).fetchone()

    if not group:
        db.close()
        return "Group not found", 404

    pref_rows = cursor.execute("""
        SELECT preference, COUNT(*) AS cnt
        FROM Users
        WHERE uID IN (
            SELECT uID
            FROM Group_members
            WHERE gID = ?
    )
    AND preference IS NOT NULL
    AND TRIM(preference) <> ''
    GROUP BY preference
    ORDER BY cnt DESC;
    """, (gID,)).fetchall()

    top_preferences = []
    if pref_rows:
        max_cnt = pref_rows[0]["cnt"]
        top_preferences = [r["preference"] for r in pref_rows if r["cnt"] == max_cnt]

    with open("sql/common_dates.sql", "r", encoding="utf-8") as f:
        common_sql = f.read()
    common_dates = cursor.execute(common_sql, (gID, gID)).fetchall()

    if not common_dates:
        db.close()
        return render_template(
            "recommend.html",
            group=group,
            months=[],
            rows=[],
            top_preferences=top_preferences,
            has_preference_match=False
        )

    months = sorted({int(row["date"].split("-")[1]) for row in common_dates})

    budget_level = group["budget"] if group["budget"] is not None else 5
    placeholders = ",".join("?" for _ in months)

    query = f"""
        SELECT DISTINCT d.dest_Name, d.country, d.Dest_type, d.Dest_cost
        FROM Destinations d
        WHERE d.destID IN (
            SELECT destID FROM RecommendMonth
            WHERE month IN ({placeholders})
        )
        AND d.Dest_cost <= ?
        ORDER BY d.Dest_cost, d.dest_Name;
    """
    rows = cursor.execute(query, (*months, budget_level)).fetchall()

    has_preference_match = False
    if top_preferences:
        has_preference_match = any(r["Dest_type"] in top_preferences for r in rows)

    db.close()
    return render_template(
        "recommend.html",
        group=group,
        months=months,
        rows=rows,
        top_preferences=top_preferences,
        has_preference_match=has_preference_match
    )

#첫 페이지
@app.route("/")
def index():
    db = sqlite3.connect("db.sqlite")
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    groups = cur.execute("SELECT gID, gName FROM Groups").fetchall()
    users = cur.execute("SELECT uID, uName FROM Users").fetchall()

    db.close()
    return render_template("index.html", groups=groups, users=users)
#그룹 상세페이지
@app.route("/groups/<int:gID>")
def groupDetail(gID):
    db = sqlite3.connect("db.sqlite")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    group = cursor.execute(
        "SELECT gID, gName, budget, cnt_members FROM Groups WHERE gID = ?",
        (gID,)
    ).fetchone()

    if not group:
        db.close()
        return "Group not found", 404

    members = cursor.execute("""
        SELECT uID, uName
        FROM Users
        WHERE uID IN (
            SELECT uID
            FROM Group_members
            WHERE gID = ?
        )
        ORDER BY uName;
    """, (gID,)).fetchall()

    db.close()
    return render_template("group_detail.html", group=group, members=members)
#그룹 날짜페이지
@app.route("/groups/<int:gID>/dates/")
def groupDates(gID):
    db = sqlite3.connect("db.sqlite")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    group = cursor.execute(
        "SELECT gID, gName, budget, cnt_members FROM Groups WHERE gID = ?",
        (gID,)
    ).fetchone()

    if not group:
        db.close()
        return "Group not found", 404

    dates = cursor.execute("""
    SELECT d.dateID, u.uName, d.date
    FROM UDate d, Users u
    WHERE d.uID = u.uID
        AND d.uID IN (
            SELECT uID
            FROM Group_members
            WHERE gID = ?
        )
    ORDER BY d.date, u.uName;
    """, (gID,)).fetchall()


    db.close()
    return render_template("group_dates.html", group=group, dates=dates, gID=gID)

#삭제
@app.route("/groups/<int:gID>/delete/", methods=["POST"])
def deleteGroup(gID):
    next_url = request.form.get("next_url", "/")
    db = sqlite3.connect("db.sqlite")
    cur = db.cursor()
    cur.execute("DELETE FROM Groups WHERE gID=?", (gID,))
    db.commit()
    db.close()
    return redirect(next_url)

@app.route("/users/<int:uID>/delete/", methods=["POST"])
def deleteUser(uID):
    next_url = request.form.get("next_url", "/")
    db = sqlite3.connect("db.sqlite")
    cur = db.cursor()
    cur.execute("DELETE FROM Users WHERE uID=?", (uID,))
    db.commit()
    db.close()
    return redirect(next_url)

@app.route("/dates/<int:dateID>/delete/", methods=["POST"])
def deleteDate(dateID):
    next_url = request.form.get("next_url", "/") 
    db = sqlite3.connect("db.sqlite")
    cur = db.cursor()
    cur.execute("DELETE FROM UDate WHERE dateID = ?", (dateID,))
    db.commit()
    db.close()
    return redirect(next_url)

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1',port=5000)