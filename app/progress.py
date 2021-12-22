from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
import sys
from werkzeug.exceptions import abort
from app.auth import login_required
from app.db import connect_db
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.io import curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.plotting import figure, output_file, show
from bokeh.resources import CDN
from bokeh.embed import file_html

bp = Blueprint('progress', __name__)

@bp.route('/analytics', methods=('GET', 'POST'))
@login_required
def analytics():

    source = ColumnDataSource()

    fig = figure(plot_height=600, plot_width=720, tooltips=[("Weight", "@weight"), ("Date", "@date")])
    fig.circle(x="x", y="y", source=source, size=5, color="color", line_color=None)
    fig.xaxis.axis_label = "Weight Lifted"
    fig.yaxis.axis_label = "Reps"
    
    user = g.user['id']
    user_data = get_user_data(user)

    # print(user_data, file=sys.stderr)
    # {'Weight': 300, 'RPE': 2, 'Lift': 'Squat', 'Reps': '3', 'Datestamp': datetime.date(2021, 12, 1), 'creator_id': 4}

    source.data = dict(
        x = [d['Weight'] for d in user_data],
        y = [d['Reps'] for d in user_data],
        RPE = [d['RPE'] for d in user_data],
        color = ["#FF9900" for d in user_data],
        lift = [d['Lift'] for d in user_data],
        date = [d['Datestamp'] for d in user_data],
        username = [d['Username'] for d in user_data],
    )

    script, div = components(fig)
    return render_template(
        'progress/dashboard.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    ).encode(encoding='UTF-8')

def get_user_data(id):
    connection = connect_db()
    cur = connection.cursor()
    query = "SELECT Weight, RPE, Lift, Reps, Datestamp, Username FROM Lifts l JOIN Users u ON l.creator_id = u.id WHERE u.id = %s" % id   
    cur.execute(query)
    workouts = cur.fetchall()
    if workouts is None:
        abort(404, "Try adding workouts first!")
    return workouts

