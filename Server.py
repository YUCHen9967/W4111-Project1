import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response,flash
from sqlalchemy.testing import db

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app = Flask(__name__)

DB_USER = "sw3509"
DB_PASSWORD = "6713"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_SERVER + "/proj1part2"

engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request
    The variable g is globally accessible
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback;
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


@app.route('/')
def home():  # put application's code here
    return render_template("home.html")

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        print(email)
        query = "SELECT COUNT(*) FROM Users AS U WHERE U.email = '{}'".format(email)
        user = g.conn.execute(query).fetchone()[0]
        if user <1:
            query = "SELECT COUNT(*) FROM admin AS a WHERE a.email = '{0}'".format(email)
            admin = g.conn.execute(query).fetchone()[0]
            if admin < 1:
                return redirect('/wrong')
            else:
                return render_template('admin.html')
        else:
            query1="WITH tmp1(userid) AS (SELECT userid FROM Users WHERE email='{0}') SELECT M.Name FROM MOVIES AS M,(SELECT MC.mid FROM Movie_collection AS MC, tmp1 AS U WHERE U.userid=MC.userid) AS tmp WHERE M.mid=tmp.mid".format(email)
            cursor = g.conn.execute(query1)
            movies = []
            for result in cursor:
                print(result)
                movies.append(result[0])  # can also be accessed using result[0]
            cursor.close()
            print(movies)
            context = dict(data=movies)
            return render_template('user.html', **context)

    return render_template("login.html")

@app.route('/add_collection',methods=('GET', 'POST'))
def add_collection():
    if request.method == 'POST':
        email = request.form['email']
        movietitle=request.form['movie']
        error=None

        query1 = "SELECT COUNT(*) FROM Users WHERE email = '{0}'".format(email)
        query2 = "SELECT COUNT(*) FROM MOVIES WHERE Name = '{0}'".format(movietitle)
        usercheck=g.conn.execute(query1).fetchone()
        moviecheck=g.conn.execute(query2).fetchone()
        if usercheck is None:
            error = 'User is already registered.'
            return render_template('wrong.html')
        elif moviecheck is None:
            error = 'No such movie.'
            return render_template('wronguser.html')

        query3 = "SELECT userid FROM Users WHERE email = '{0}'".format(email)
        query4 = "SELECT mid FROM MOVIES WHERE Name = '{0}'".format(movietitle)

        mid=0
        userid=0
        cursor = g.conn.execute(query3)
        for result in cursor:
            print(result)
            userid=result[0]
        cursor.close()
        cursor = g.conn.execute(query4)
        for result in cursor:
            mid=result[0]
        cursor.close()


        if error is None:
            query = "INSERT INTO Movie_collection (userid, mid) VALUES ('{0}','{1}')".format(userid, mid)
            g.conn.execute(query)
            return redirect(request.referrer)
    return render_template("add_collection.html")

@app.route('/searchcele',methods=('GET', 'POST'))
def searchcele():
    if request.method == 'POST':
        email = request.form['email']
        search = request.form['search']
        query1 = "SELECT COUNT(*) FROM Users WHERE email = '{0}'".format(email)
        usercheck = g.conn.execute(query1).fetchone()[0]
        if usercheck<1:
            error = 'User is already registered.'
            return render_template('wrong.html')
        else:
            query1="SELECT userid FROM Users WHERE email = '{0}'".format(email)
            userid=0
            cursor=g.conn.execute(query1)
            for result in cursor:
                userid=result[0]  # can also be accessed using result[0]
            cursor.close()
        query3 = "SELECT COUNT(*) FROM Celebrity WHERE name = '{0}'".format(search)
        celebritycheck = g.conn.execute(query3).fetchone()[0]
        if celebritycheck<1:
            return render_template('wrongcele.html')
        else:
            query3 = "SELECT * FROM Celebrity WHERE name='{0}'".format(search)
            cursor = g.conn.execute(query3)
            Celebrity = []
            for result in cursor:
                Celebrity.append(result['name'])  # can also be accessed using result[0]
            cursor.close()
            query4 = "SELECT celeid FROM Celebrity WHERE name = '{0}'".format(search)
            cursor = g.conn.execute(query4)
            celeid=0
            for result in cursor:
                celeid=result[0]  # can also be accessed using result[0]
            cursor.close()
            query5 = "INSERT INTO Search_celebrity (userid, celeid) VALUES ('{0}','{1}')".format(userid, celeid)
            g.conn.execute(query5)
            context = dict(data=Celebrity)
            return render_template("celebrity.html", **context)
    return render_template("search.html")

@app.route('/searchmovie',methods=('GET', 'POST'))
def searchmovie():
    if request.method == 'POST':
        email = request.form['email']
        search = request.form['search']
        query1 = "SELECT COUNT(*) FROM Users WHERE email = '{0}'".format(email)
        usercheck = g.conn.execute(query1).fetchone()[0]
        if usercheck<1:
            return render_template('wrong.html')
        else:
            query1="SELECT userid FROM Users WHERE email = '{0}'".format(email)
            userid=0
            cursor=g.conn.execute(query1)
            for result in cursor:
                userid=result[0]  # can also be accessed using result[0]
            cursor.close()
        query2 = "SELECT COUNT(*) FROM MOVIES WHERE Name = '{0}'".format(search)

        moviecheck = g.conn.execute(query2).fetchone()[0]
        print(moviecheck)
        if moviecheck<1:
            return render_template('wronguser.html')
        else:
            query5 = "SELECT * FROM MOVIES WHERE Name='{0}'".format(search)
            cursor=g.conn.execute(query5)
            movieTitle = ""
            movieDetail = 0
            movieStoryline = 0
            moviegenre = 0
            movieid = 0

            for result in cursor:
                movieTitle = result['name']
                movieDetail = result["details"]
                movieStoryline = result["storyline"]
                moviegenre = result['genre']
                movieid = result['mid']
            cursor.close()
            movierate = ""
            query = "SELECT round(avg(UR.rate),1) AS rate FROM User_rate AS UR WHERE UR.mid='{0}'".format(movieid)
            cursor = g.conn.execute(query)
            for result in cursor:
                movierate = result['rate']
            cursor.close()

            query = "SELECT C1.name FROM Celebrity AS C1, (SELECT celeid FROM Act AS A WHERE A.mid='{0}') AS C2 WHERE C1.celeid=C2.celeid".format(
                movieid)
            cursor = g.conn.execute(query)
            actors = []
            cursor = g.conn.execute(query)
            for result in cursor:
                actors.append(result[0])
            cursor.close()
            query = "SELECT DISTINCT U.username, UC.comment FROM Users AS U, User_comment AS UC WHERE UC.mid='{0}' AND U.userid=UC.userid".format(
                movieid)
            cursor = g.conn.execute(query)
            Comment = []
            Username = []
            cursor = g.conn.execute(query)
            for result in cursor:
                Username.append(result[0])
                Comment.append(result[1])
            cursor.close()
            query5 = "INSERT INTO Search(userid, mid) VALUES ('{0}','{1}')".format(userid, movieid)
            g.conn.execute(query5)
        return render_template("movie1.html", title=movieTitle, Detail=movieDetail,
                               Storyline=movieStoryline, actors=actors,
                               genre=moviegenre, rate=movierate, comments=Comment, Username=Username)
    return render_template("search.html")

@app.route('/wrong')
def wrong():
    return render_template("wrong.html")


@app.route('/movies')
def Movies():
    cursor = g.conn.execute("SELECT * FROM MOVIES AS M ")
    movies = []
    for result in cursor:
        movies.append(result['name'])  # can also be accessed using result[0]
    cursor.close()

    context = dict(data=movies)
    return render_template("Movies.html", **context)


@app.route('/movies/<name>')
def movie(name):
    query = "SElECT * FROM Movies AS m WHERE m.name= '{0}'".format(
        name)
    cursor = g.conn.execute(query)
    movieTitle = ""
    movieDetail = 0
    movieStoryline = 0
    moviegenre = 0
    movieid = 0

    for result in cursor:
        movieTitle = result['name']
        movieDetail = result["details"]
        movieStoryline = result["storyline"]
        moviegenre = result['genre']
        movieid = result['mid']
    cursor.close()

    movierate = ""
    query = "SELECT round(avg(UR.rate),1) AS rate FROM User_rate AS UR WHERE UR.mid='{0}'".format(movieid)
    cursor = g.conn.execute(query)
    for result in cursor:
        movierate = result['rate']
    cursor.close()

    query = "SELECT C1.name FROM Celebrity AS C1, (SELECT celeid FROM Act AS A WHERE A.mid='{0}') AS C2 WHERE C1.celeid=C2.celeid".format(
        movieid)
    cursor = g.conn.execute(query)
    actors = []
    cursor = g.conn.execute(query)
    for result in cursor:
        actors.append(result[0])
    cursor.close()
    query = "SELECT DISTINCT U.username, UC.comment FROM Users AS U, User_comment AS UC WHERE UC.mid='{0}' AND U.userid=UC.userid".format(
        movieid)
    cursor = g.conn.execute(query)
    Comment = []
    Username=[]
    cursor = g.conn.execute(query)
    for result in cursor:
        Username.append(result[0])
        Comment.append(result[1])
    cursor.close()
    return render_template("movie.html", title=movieTitle, Detail=movieDetail,
                           Storyline=movieStoryline, actors=actors,
                           genre=moviegenre, rate=movierate,comments=Comment,Username=Username)

@app.route('/movies/comment',methods=('GET', 'POST'))
def comment():
    if request.method == 'POST':
        email = request.form['email']
        movietitle=request.form['movie']
        comment=request.form['comment']
        error=None

        query1 = "SELECT COUNT(*) FROM Users WHERE email = '{0}'".format(email)
        query2 = "SELECT COUNT(*) FROM MOVIES WHERE Name = '{0}'".format(movietitle)
        usercheck=g.conn.execute(query1).fetchone()
        moviecheck=g.conn.execute(query2).fetchone()
        if usercheck is None:
            error = 'User is already registered.'
            return render_template('wrong.html')
        elif moviecheck is None:
            error = 'No such movie.'
            return render_template('wronguser.html')

        query3 = "SELECT userid FROM Users WHERE email = '{0}'".format(email)
        query4 = "SELECT mid FROM MOVIES WHERE Name = '{0}'".format(movietitle)
        query5 = "SELECT count(*) FROM User_comment "
        mid=0
        userid=0
        cursor = g.conn.execute(query3)
        for result in cursor:
            print(result)
            userid=result[0]
        cursor.close()
        cursor = g.conn.execute(query4)
        for result in cursor:
            mid=result[0]
        cursor.close()
        cid=0
        cursor = g.conn.execute(query5)
        for result in cursor:
            cid=result[0]
        cursor.close()
        cid=cid+1
        print(cid,userid,mid)
        if error is None:
            query = "INSERT INTO User_comment (cid, userid, mid, comment) VALUES ('{0}','{1}','{2}','{3}')".format(
                cid, userid, mid, comment)
            g.conn.execute(query)
            return redirect(request.referrer)

    return render_template('comment.html')

@app.route('/celebrity')
def Celebrity():
    cursor = g.conn.execute("SELECT * FROM Celebrity ")
    Celebrity = []
    for result in cursor:
        Celebrity.append(result['name'])  # can also be accessed using result[0]
    cursor.close()

    context = dict(data=Celebrity)
    return render_template("celebrity.html", **context)

@app.route('/News')
def News():
    cursor = g.conn.execute("SELECT * FROM Movie_news ")
    title=[]
    for result in cursor:
        title.append(result['title'])  # can also be accessed using result[0]
    cursor.close()
    context = dict(data=title)
    return render_template("news.html", **context)

@app.route('/star/<name>')
def star(name):
    query = "SElECT * FROM Celebrity AS c WHERE c.name= '{0}'".format(
        name)
    cursor = g.conn.execute(query)
    celebrityname = ""
    detail = 0

    for result in cursor:
        celebrityname = result['name']
        detail = result["details"]

    cursor.close()
    return render_template("star.html", name=celebrityname, Detail=detail)

@app.route('/add_movies',method=('GET', 'POST'))
def add_movies():
    if request.method == 'POST':
        email = request.form['email']
        movietitle=request.form['movie']
        movieDetail = request.form["detail"]
        movieStoryline = request.form["storyline"]
        moviegenre = request.form['genre']
        error=None

        query1 = "SELECT COUNT(*) FROM Admin WHERE email = '{0}'".format(email)
        query2 = "SELECT COUNT(*) FROM MOVIES WHERE Name = '{0}'".format(movietitle)
        usercheck=g.conn.execute(query1).fetchone()[0]
        moviecheck=g.conn.execute(query2).fetchone()[0]
        if usercheck <1:
            error = 'User is already registered.'
            return render_template('wrong.html')
        if moviecheck ==1:
            error= 'Movie has been submitted.'
            return render_template('moviesubmitted.html')
        query3 = "SELECT COUNT(*) FROM MOVIES"
        query4 = "SELECT aid FROM Admin WHERE email = '{0}'".format(email)

        mid=0
        aid=0
        cursor = g.conn.execute(query4)
        for result in cursor:
            aid=result[0]
        cursor.close()

        cursor = g.conn.execute(query3)

        for result in cursor:
            mid=result[0]
        cursor.close()
        mid=mid+1


        if error is None:
            query5 = "INSERT INTO adjust_Movie (aid,mid) VALUES ('{0}','{1}')".format(aid,mid)
            query6="INSERT INTO MOVIES (mid,Name,Details,Genre,Storyline) VALUES ('{0}','{1}','{2}','{3}','{4}')".format(mid,movietitle,movieDetail,moviegenre,movieStoryline)
            g.conn.execute(query5)
            g.conn.execute(query6)

            return redirect(request.referrer)
    return render_template("add_movies.html")

@app.route('/add_celebrity',method=('GET', 'POST'))
def add_celebrity():
    if request.method == 'POST':
        email = request.form['email']
        movietitle = request.form['movie']
        name = request.form["name"]
        detail = request.form["detail"]
        error=None
        query1 = "SELECT COUNT(*) FROM Admin WHERE email = '{0}'".format(email)
        query2 = "SELECT COUNT(*) FROM Celebrity WHERE name = '{0}'".format(name)
        usercheck = g.conn.execute(query1).fetchone()[0]
        celebritycheck = g.conn.execute(query2).fetchone()[0]
        if usercheck < 1:
            error = 'User is already registered.'
            return render_template('wrong.html')
        if celebritycheck == 1:
            error = 'Movie has been submitted.'
            return render_template('moviesubmitted.html')
        query3 = "SELECT COUNT(*) FROM Celebrity"
        query4 = "SELECT aid FROM Admin WHERE email = '{0}'".format(email)
        cid=0
        cursor = g.conn.execute(query3)
        for result in cursor:
            cid = result[0]
        cursor.close()
        cid=cid+1

        aid=0
        cursor = g.conn.execute(query4)
        for result in cursor:
            aid = result[0]
        cursor.close()
        query5="SELECT mid FROM MOVIES WHERE Name='{0}'".format(movietitle)
        mid=0
        cursor = g.conn.execute(query4)
        for result in cursor:
            mid = result[0]
        cursor.close()

        query6 = "SELECT COUNT(*) FROM MOVIES WHERE Name = '{0}'".format(movietitle)
        moviecheck = g.conn.execute(query6).fetchone()[0]
        if moviecheck<1:
            error = 'User is already registered.'
            return render_template('wronguser.html')
        if error is None:
            query="INSERT INTO Celebrity(celeid, name, details) VALUES ('{0}','{1}','{2}')".format(cid,name,detail)
            g.conn.execute(query)
            query = "INSERT INTO Act(mid, celeid) VALUES ('{0}','{1}')".format(mid, cid)
            g.conn.execute(query)
            query="INSERT INTO Adjust_celebrity(aid,celeid) VALUES('{0}','{1}')".format(aid, cid)
            g.conn.execute(query)
            return redirect(request.referrer)
    return render_template('add_celebrity.html')



if __name__ == '__main__':
    app.run()
