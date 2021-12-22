from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from app.auth import login_required
from app.db import connect_db
import sys

bp = Blueprint('feed', __name__)

@bp.route('/')
@login_required
def index():
    connection = connect_db()
    user = g.user['id']
    #user = '1'
    query = "SELECT l.id, l.creator_id, FirstName, username, Weight, RPE, Lift, Reps, Datestamp FROM Lifts l JOIN Users u ON l.creator_id = u.id WHERE u.id = '%s' ORDER BY Datestamp DESC;" % user
    
    cur = connection.cursor()
    cur.execute(query)
    workouts = cur.fetchall()

    return render_template('feed/index.html', workouts=workouts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        lift = request.form['Lift']
        weight = request.form['Weight']
        reps = request.form['Reps']
        RPE = request.form['RPE']
        date = request.form['Date']
        user = g.user['id']
        error = None

        if not user:
            error = 'Sign in again'
        elif not lift or lift=="None":
            error = "Enter a lift!"
        elif not reps:
            error = 'Reps are required.'
        elif not RPE:
            error = 'RPE is required.'
        elif not date:  
            error = 'Date is required.'
        elif not weight:  
            error = 'Weight is required.'

        if error is None:
            try:
                query = "INSERT INTO Lifts(creator_id, Weight, RPE, Lift, Reps, Datestamp) VALUES('%s', '%s', '%s', '%s', '%s', '%s');" % (user, weight, RPE, lift, reps, date)

                connection = connect_db()
                cur = connection.cursor()
                cur.execute(query)
                connection.commit()
                cur.close()
                return redirect(url_for('index'))
            except:
                flash("Value out of range - nice try!")
        else:
            flash(error)

    return render_template('feed/create.html')

def get_workout(id, check_author=True):
    connection = connect_db()
    cur = connection.cursor()
    query = "SELECT l.id, Weight, RPE, Lift, Reps, Datestamp, creator_id FROM Lifts l JOIN Users u ON l.creator_id = u.id WHERE l.id = %s" % id   
    cur.execute(query)
    workout = cur.fetchone()

    if workout is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and workout['creator_id'] != g.user['id']:
        abort(403)

    return workout

# insert update function
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    workout = get_workout(id)

    if request.method == 'POST':
        lift = request.form['Lift']
        weight = request.form['Weight']
        reps = request.form['Reps']
        RPE = request.form['RPE']
        date = request.form['Date']

        error = None

        if not lift:
            error = "Enter a lift!"
        elif not reps:
            error = 'Reps are required.'
        elif not RPE:
            error = 'RPE is required.'
        elif not date:  
            error = 'Date is required.'
        elif not weight:  
            error = 'Weight is required.'

        if error is not None:
            flash(error)
        else:
            connection = connect_db()
            cur = connection.cursor()
            query = "UPDATE Lifts SET Lift='%s', RPE='%s', Reps='%s', Datestamp='%s', Weight='%s' WHERE id = '%s';" % (lift, RPE, reps, date, weight, id)
            cur.execute(query)
            connection.commit()
            cur.close()
            return redirect(url_for('index'))

    return render_template('feed/update.html', workout=workout)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_workout(id)
    connection = connect_db()
    cur = connection.cursor()
    query = "DElETE FROM Lifts where id=%s" % id
    cur.execute(query)
    connection.commit()
    cur.close()
    return redirect(url_for('index'))
