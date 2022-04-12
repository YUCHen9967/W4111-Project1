import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app = Flask(__name__)

DB_USER = "sw3509"
DB_PASSWORD = "6713"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"

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
    import traceback; traceback.print_exc()
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
        username = request.form['email']
        query = "SELECT * FROM Users AS U WHERE U.email = '{}'".format(username)
        user = g.conn.execute(query).fetchone()

        if user is None:
            query = "SELECT * FROM admin AS a WHERE a.email = '{}'".format(username)
            admin = g.conn.execute(query).fetchone()
            if admin is None:
                return redirect('/wrong')
            else:
                return redirect('/')
        else:
            return redirect('/')
    return render_template("login.html")
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
    return render_template("Movies.html",**context)


@app.route('/movies/<name>')
def movie(name):
    query = "SElECT * FROM Movies AS m WHERE m.name= '{0}'".format(
        name)
    cursor = g.conn.execute(query)
    movieTitle = ""
    movieDetail = 0
    movieStoryline = 0
    moviegenre= 0
    movieid=0


    for result in cursor:
        movieTitle = result['name']
        movieDetail = result["details"]
        movieStoryline = result["storyline"]
        moviegenre= result['genre']
        movieid=result['mid']
    cursor.close()

    movierate = ""
    query="SELECT round(avg(UR.rate),1) AS rate FROM User_rate AS UR WHERE UR.mid='{0}'".format(movieid)
    cursor = g.conn.execute(query)
    for result in cursor:
        movierate= result['rate']
    cursor.close()

    query = "SELECT C1.name FROM Celebrity AS C1, (SELECT celeid FROM Act AS A WHERE A.mid='{0}') AS C2 WHERE C1.celeid=C2.celeid".format(movieid)
    cursor = g.conn.execute(query)
    actors = []
    cursor = g.conn.execute(query)
    for result in cursor:
        actors.append(result[0])
    cursor.close()
    return render_template("movie.html", title=movieTitle, Detail=movieDetail,
                           Storyline=movieStoryline,actors=actors,
                           genre=moviegenre,rate=movierate)





@app.route('/celebrity')
def Celebrity():
    cursor = g.conn.execute("SELECT * FROM Celebrity ")
    Celebrity = []
    for result in cursor:
        Celebrity.append(result['name'])  # can also be accessed using result[0]
    cursor.close()

    context = dict(data=Celebrity)
    return render_template("celebrity.html",**context)

@app.route('/star/<name>')
def star(name):
    query = "SElECT * FROM Celebrity AS c WHERE c.name= '{0}'".format(
        name)
    cursor = g.conn.execute(query)
    celebrityname= ""
    detail = 0

    for result in cursor:
        celebrityname = result['name']
        detail = result["details"]

    cursor.close()
    return render_template("star.html",name=celebrityname,Detail=detail)

@app.route('/News')
def News():
    cursor = g.conn.execute("SELECT * FROM Movie_news ")
    title=[]
    for result in cursor:
        title.append(result['title'])  # can also be accessed using result[0]
    cursor.close()
    context = dict(data=title)
    return render_template("news.html", **context)


@app.route('/login')
def login():
  return render_template("login.html")
@app.route('/user')
def user():
  return render_template("user.html")
@app.route('/admin')
def admin():
  return render_template("admin.html")

if __name__ == '__main__':
    app.run()
