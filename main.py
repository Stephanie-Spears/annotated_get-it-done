from flask import Flask, request, redirect, render_template
#SQLAlchemy is a class that enables Python applications to "talk to" databases. It is able to work with several SQL-based database engines.
#
# The flask_sqlalchemy module is a "wrapper" of SQLAlchemy that makes it work more seemlessly with Flask applications.
#
# To install flask-sqlalchemy within a conda environment, use:
#
# (flask-env) $ conda install -c conda-forge flask-sqlalchemy
# And while you're at it, install the pymyql module, which we'll use (and explain) below:
#
# (flask-env) $ conda install pymysql
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
# This line adds a new entry to the app.config dictionary, with key 'SQLALCHEMY_DATABASE_URI. The SQLAlchemy module will use this string to connect to our MySQL database.
#
# This string is a regular source of database connection problems. If any portion of it isn't exactly correct, our app won't be able to connect properly.
#
# The components of this connection string are, from left to right:
#
# mysql - specifies that we'll be using a MySQL database
# pymysql - specifies that we'll be using the pymysql database driver. A database driver is the mechanism by which an application can "talk to" a database.
# get-it-done:beproductive - specifies the database user and password to be used to connect. The user must already exist, and must have correct permissions on the given database.
# @localhost - specifies that we'll connect to a database on our local computer. If we were connecting to a remote database, we'd put the host name or IP address here.
# :8889 - specifies the port that the database is expected to be running on. Production MySQL databases typically run on port 3306, but our development database will run on a different port. Having the incorrect port is a common connection problem. You can check your port by looking at the Preferences or Settings pane of MAMP.
# /get-it-done - the name of the database that we'll use. This database must already exist (but can be empty) and the user we specified must have all (or most) permissions on the database.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:beproductive@localhost:8889/get-it-done'
# Enabling this setting will turn on query logging. In other words, when our app does anything that results in a database query being executed, the query that SQLAlchemy generates and executes will be logged to the terminal that our app is running within.
#
# This can be very useful in understanding how SQLAlchemy works, and what happens within an ORM library.
app.config['SQLALCHEMY_ECHO'] = True
# Create a database connection and interface for our app. We'll use the db object throughout our app, and it will allow us to interact with the database via our Flask/Python code.
db = SQLAlchemy(app)

# Creates a class that extends the db.Model class. By extending this class, we'll get a lot of functionality that will allow our class to be managed by SQLAlchemy, and thus stored in the database.
class Task(db.Model):
# Creates a new property of our class that will map to an integer column in the task table. The column name will be generated from the property name to be id as well. The column will be a primary key column on the table.
    id = db.Column(db.Integer, primary_key=True)
    # Creates a property that will map to a column of type VARCHAR(120) in the task table.
    name = db.Column(db.String(120))
    # Creates a property completed that will map to a column of type BOOL, which is actually a TINYINT column with a constraint that it can only hold 0 or 1.
    completed = db.Column(db.Boolean)

    def __init__(self, name):
        self.name = name
        self.completed = False


@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        task_name = request.form['task']
        # To create an instance of our persistent Task class, we use the same syntax as always.
        new_task = Task(task_name)
# Our ORM system, SQLAlchemy, does not know about our new object until we notify it that we want our object to be stored in the database. This is done by calling db.session.add().
#
# A database session can be thought of as a collection of queries to be run all at once, when we ask the database to commit the session.
        db.session.add(new_task)
        # Our changes and additions to the database aren't actually run against the database until we commit the session.
        #
        db.session.commit()
# Every class that extends db.Model will have a query property attached to it. This query object contains lots of useful methods for querying the database for data from the associate table(s).
#
# Here, Task.query.all() has the net effect of running
#
# SELECT * FROM task
# and then taking the results and turning them into a list of Task objects.
    tasks = Task.query.filter_by(completed=False).all()
    completed_tasks = Task.query.filter_by(completed=True).all()
    return render_template('todos.html',title="Get It Done!",
        tasks=tasks, completed_tasks=completed_tasks)


@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    # Calling query.get() will query for the specific object/row by it's primary key.
    task = Task.query.get(task_id)
    task.completed = True
    # In order to save the changes to the given object to the database, we need to add and commit.
    db.session.add(task)
    db.session.commit()

    return redirect('/')

# We added this conditional to allow us to import objects and classes from code outside of this file in a way that doesn't run the application. In particular, we'll want to import db and Task within a Python shell.
#
# Without this check, when importing these items in another setting, app.run() would be called, starting up the application server. In those situations, we do not want that to happen.
if __name__ == '__main__':
    app.run()
