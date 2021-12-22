import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from . import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        password = request.form['password']
        email = request.form['email']
                    

        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'
        elif not firstName:
            error = 'First name is required.'
        elif not lastName:  
            error = 'Last name is required.'


        if error is None:
            try:
                connection = db.connect_db()
                cur = connection.cursor()
                query = "INSERT INTO Users(FirstName, LastName, Email, Username, Password) VALUES('%s', '%s', '%s', '%s', '%s');" % (firstName, lastName, email, username, generate_password_hash(password))
                cur.execute(query)
                connection.commit()
                cur.close()
            except:
                flash(f"Try again, some stole the username {username}")
            else:
                return redirect(url_for("auth.login"))
        else:
            flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        connection = db.connect_db()
        cur = connection.cursor()
        query = "SELECT * FROM Users WHERE Username = '%s';" % username
        cur.execute(query)
        result = cur.fetchone()
        # result = cur.fetchone()
        cur.close()
        
        if result is None:
            error = 'Incorrect username.'
        elif not check_password_hash(result['Password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = result['id']
            return redirect(url_for('index'))
        else:
            flash(error)
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None # May be some problems using g here!!!
    else:
        cur = db.connect_db().cursor()
        cur.execute('SELECT * FROM users WHERE id = %s' % user_id)
        g.user = cur.fetchone()
        cur.close()


@bp.route('/logout')
def logout(): 
    session.clear()
    return redirect(url_for('index'))

def login_required(view): # Wrapper to check if user is logged in before executing other functions
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view