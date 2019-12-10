# todo: write method to save form files
from app.augmd import bp
from app.augmd.forms import FileForm
from werkzeug.utils import secure_filename
import os
from flask import render_template, send_file, flash, current_app
import pandas as pd
import numpy as np
from tempfile import mkstemp
from zipfile import ZipFile


@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])
def index():
    form = FileForm()
    if form.validate_on_submit():
        md = pd.read_excel(save_excel(form.max_diff_data.data, 'md'))
        rank = pd.read_excel(save_excel(form.ranking_data.data, 'rank'))
        design = pd.read_excel(save_excel(form.design.data, 'design'))
        wl_rates = list(pd.read_excel(save_excel(form.win_loss_rates.data, 'wl_rates'))['Wins'].values)
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
        
    return render_template('augmd/index.html', title="Augmented MaxDiff", form=form)


def save_excel(data, name):
    if not os.path.exists(current_app.instance_path):
        os.mkdir(current_app.instance_path)
    if not os.path.exists(os.path.join(current_app.instance_path, 'files')):
        os.mkdir(os.path.join(current_app.instance_path, 'files'))
    filename = os.path.join(current_app.instance_path, 'files', f'{name}.xlsx')
    data.save(filename)
    return filename

def prep(md, rank):
    # md file
    w_cols =  [col for col in md if col.startswith("*MDWORST")] ## Include support for custom prefix or set format
    b_cols =  [col for col in md if col.startswith("*MDBEST")]

    ordered_bw = []
    for i in range(0, len(b_cols)):
        ordered_bw.append(b_cols[i])
        ordered_bw.append(w_cols[i])

    md_cols = ['responseid', 'respid', 'hVersion'] + ordered_bw

    final_md = md[md_cols].copy()
    md_col_names = ['responseid','respid','maxdiffversion']
    for i in range(1, len(b_cols)+1):
        md_col_names.append(f'B{i}')
        md_col_names.append(f'W{i}')
    final_md.columns = md_col_names

    # rank file

    #r_cols = [col for col in rank if col.startswith('*RANK')]
    b_ranks = [col for col in rank if col.startswith('*RANKBEST')]
    w_ranks = [col for col in rank if col.startswith('*RANKWORST')]

    rank_data = {}
    for i in range(0, len(rank)):
        best_ranks = rank[b_ranks].loc[i][(~rank[b_ranks].loc[i].isna())].sort_values()
        best_list = [int(item.split('_')[1]) for item in best_ranks.index]

        worst_ranks = rank[w_ranks].loc[i][(~rank[w_ranks].loc[i].isna())].sort_values()
        worst_list = [int(item.split('_')[1]) for item in worst_ranks.index]

        rank_data[ rank.loc[i]['respid'] ] = best_list + worst_list

    rank_col_names = []
    rank_col_names += [f'Best{i}' for i in range(1, len(best_list)+1)]
    rank_col_names += [f'Worst{i}' for i in range(1, len(worst_list)+1)]

    final_ranks = pd.DataFrame.from_dict(rank_data, orient='index', columns=rank_col_names)
    final_ranks.reset_index(inplace = True)
    final_ranks.columns = ['respid'] + list(final_ranks.columns[1:])

    final_ranks.head(1)

    ## Merge MD and Rank files
    final_prepped = final_md.merge(final_ranks,on='respid',how='outer')
    final_prepped.set_index('responseid', inplace = True)
    
    return final_prepped

def pairs(data, design, wl_rates):
    md_tasks = max([int(col[1:]) for col in data.columns if col.startswith('B') and len(col)< 4])
    ranked_items = max([int(col[4:]) for col in data.columns if col.startswith('Best')])
    rank_cols = data.columns[-ranked_items*2:]
    md_cols = [col for col in data.columns if len(col) < 5]

    streamlined_data = []
    streamlined_cols = ['CaseID', 'Set', 'Position', 'Items', 'Response']
    key_data = []
    key_cols = ['respid', 'Choice Set', 'Item A', 'Item B']
    middle_data = []
    middle_cols = ['respid', 'Version', 'Task', 'Middle A', 'Middle B']

    for i in data.index: # for each respondent
        rank_data = data.loc[i][rank_cols]
        best_ranks = rank_data[:ranked_items]
        worst_ranks = rank_data[ranked_items:]

        # create pairs from ranks (one down)
    #     best_pairs = [[best_ranks[i], best_ranks[i+1]] for i in range(0, ranked_items-1)]
    #     worst_pairs = [[worst_ranks[i], worst_ranks[i+1]] for i in range(0, ranked_items-1)]

        # create pairs from ranks (differential)
        best_pairs = []
        worst_pairs = []
        
        # keep track of items
        best_labels = []
        worst_labels = []

        for r, best in enumerate(best_ranks): # r = rank of current item
            for w in range(0, wl_rates[r]): # wl_rates[r] = number of wins for current item
                best_pairs.append([best, best_ranks[r+1+w]])
                best_labels.append([f'Best{r+1}', f'Best{r+1+w+1}'])

        for r, worst in enumerate(worst_ranks): # r = rank of current item
            for l in range(0, wl_rates[-1-r]): # wl_rates[-1-r] = number of wins for current item (goes backwards through list)
                worst_pairs.append([worst_ranks[r-1-l], worst])
                worst_labels.append([f'Worst{r+1}', f'Worst{r-1-l+1}'])


        md_data = data.loc[i][md_cols]
        version = int( data.loc[i]['maxdiffversion'] )
        respid = int( data.loc[i]['respid'] )

        md_pairs_BvM = []
        md_pairs_MvW = []
        BvM_labels = []
        MvW_labels = []

        # create pairs from MD data
        for task in range(1, md_tasks+1):
            items = design[(design['Version'] == version) & (design['Set'] == task)].values[0][2:] # removes version and task cols, selecting only items
            items = items[~np.isnan(items)] # removes blank items

            best = md_data[(task-1)*2] # finds appropriate best data index from current task...
            worst = md_data[(task-1)*2+1] #... if current task = 2, best = 2, worst = 3  check out the structure of md_data to understand (B1, W1, B2, W2)

            middles = [item for item in items if item not in [best, worst]] # a list of all items in the design that aren't best or worst
            middle_data += [ [respid, version, task] + middles ]
#             md_pairs_BvM.append([best, worst])
#             BvM_labels.append([f'B{task}', f'W{task}'])
            for m, middle in enumerate(middles):
                md_pairs_BvM.append([best, middle])
                md_pairs_MvW.append([middle, worst])
                BvM_labels.append([f'B{task}', f'M{task}{chr(ord("A")+m)}'])
                MvW_labels.append([f'M{task}{chr(ord("A")+m)}', f'W{task}'])

        all_pairs = best_pairs + md_pairs_BvM + md_pairs_MvW + worst_pairs
        all_labels = best_labels + BvM_labels + MvW_labels + worst_labels
        
        key_data += [ [i, l+1, all_labels[l][0], all_labels[l][1]] for l in range(0, len(all_labels)) ]

        for s, pair in enumerate(all_pairs):
            streamlined_data.append([respid, s+1, 1, pair[0], 1])
            streamlined_data.append([respid, s+1, 2, pair[1], -1])

    streamlined_df = pd.DataFrame(streamlined_data, columns = streamlined_cols)
    key_df = pd.DataFrame(key_data, index=range(1, len(key_data)+1), columns=key_cols)
    key_df.set_index('respid', inplace=True)
    middle_df = pd.DataFrame(middle_data, columns=middle_cols)
    middle_df.set_index('respid', inplace=True)
                                   
    return streamlined_df, key_df, middle_df