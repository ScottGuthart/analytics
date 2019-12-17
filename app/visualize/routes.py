from app.visualize import bp
from flask_login import login_required
from app.auth.confirm import check_confirmed
from flask import render_template, request
from app.visualize.plot import create_plot
import plotly.express as px
import pygsheets

@bp.route('/distribution', methods=['GET','POST'])
@login_required
@check_confirmed
def distribution():
    #client = pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS')

    y_col = "tip"
    color_col = "sex"
    x_col = "smoker"
    df = px.data.tips()
    bar = create_plot(df, x_col, y_col, color_col)
    return render_template('visualize/distribution.html',
     plot=bar, cols = df.columns,
     y_col = y_col, color_col = color_col, x_col = x_col)

@bp.route('/update_dist', methods=['GET','POST'])
@login_required
@check_confirmed
def update_plot(x_col=None, y_col=None, color_col=None):
    y = request.args['y_col']
    x = request.args['x_col']
    color = request.args['color_col']
    graphJSON = create_plot(px.data.tips(), x, y, color)

    return graphJSON