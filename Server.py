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

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"

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
@app.route('/movies')
def Movies():
    cursor = g.conn.execute("SELECT * FROM MOVIES AS M ORDER BY M.mid")
    movies = []
    for result in cursor:
      movies.append(result[mid])  # can also be accessed using result[0]
    cursor.close()

    context = dict(data=movies)
    return render_template("Movies.html",**context)
@app.route('/celebrity')
def Celebrity():
  return render_template("celebrity.html")
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
