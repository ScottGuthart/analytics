# todo: write method to save form files
from app.augmd import bp
from app.augmd.forms import PairsForm, DesignForm
from werkzeug.utils import secure_filename
import os
from flask import render_template, send_file, flash, current_app
import pandas as pd
import numpy as np
from tempfile import mkstemp
from zipfile import ZipFile
from flask_login import login_required
from app.auth.confirm import check_confirmed
from app.augmd.pairs import prep, pairs
from app.augmd.save_user_file import save_user_file
from app.augmd.designer import designer

@bp.route('/pairs', methods=['GET','POST'])
@login_required
@check_confirmed
def create_pairs():
    form = PairsForm()
    if form.validate_on_submit():
        md = pd.read_excel(save_user_file(form.max_diff_data.data, 'md', 'xlsx'))
        rank = pd.read_excel(save_user_file(form.ranking_data.data, 'rank', 'xlsx'))
        design = pd.read_excel(save_user_file(form.design.data, 'design', 'xlsx'))
        wl_rates = list(pd.read_excel(save_user_file(form.win_loss_rates.data, 'wl_rates', 'xlsx'))['Wins'].values)
        wl_rates = [int(r) for r in wl_rates if not np.isnan(r)]
        
        data = prep(md, rank)
        streamlined, key, middle = pairs(data, design, wl_rates)
        
        zip_fn = os.path.join(current_app.instance_path, 'files', f'output.zip')
        prep_fn = os.path.join(current_app.instance_path, 'files', f'prep.csv')
        streamlined_fn = os.path.join(current_app.instance_path, 'files', f'streamlined.csv')
        key_fn = os.path.join(current_app.instance_path, 'files', f'key.csv')
        middle_fn = os.path.join(current_app.instance_path, 'files', f'middle.csv')
        
        data.to_csv(prep_fn,index=False)
        streamlined.to_csv(streamlined_fn,index=False)
        key.to_csv(key_fn)
        middle.to_csv(middle_fn)
        
        with ZipFile(zip_fn,'w') as zip: 
            for file in [prep_fn, streamlined_fn, key_fn, middle_fn]: 
                zip.write(file, os.path.basename(file)) 

        #return send_file(output_filename, mimetype='text/csv',as_attachment=True)
        return send_file(zip_fn, mimetype='application/zip',as_attachment=True)
        
    return render_template('augmd/pairs.html', title="Augmented MaxDiff Pairs", form=form)

@bp.route('/designer', methods=['GET','POST'])
@login_required
@check_confirmed
def create_design():
    form = DesignForm()
    if form.validate_on_submit():
        design = pd.read_csv(save_user_file(form.design.data, 'design', 'csv'))
        num_to_keep = form.num_to_keep.data

        design = designer(design, num_to_keep)
        output_filename = save_user_file(data=None, name='output', ext='csv')
        design.to_csv(output_filename, index=False)
        return send_file(output_filename, mimetype='text/csv',as_attachment=True)
    
    return render_template('augmd/designer.html', title="Augmented MaxDiff Designer", form=form)