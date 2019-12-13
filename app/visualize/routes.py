from app.visualize import bp
from flask_login import login_required
from app.auth.confirm import check_confirmed
from flask import render_template
from app.visualize.plot import create_plot

@bp.route('/distribution', methods=['GET','POST'])
@login_required
@check_confirmed
def distribution():
    bar = create_plot()
    return render_template('visualize/distribution.html', plot=bar)