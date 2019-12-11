import pandas as pd
from functools import reduce
import numpy as np

def designer(design, num_to_keep):
    items = [col for col in design if col.startswith('Item')]
    all_items = sorted(list(set(reduce(lambda x,y: list(x)+list(y), design[items].values.T))))

    num_to_delete = len(all_items)-num_to_keep
    items_to_delete = all_items[-num_to_delete:]
    design[items] = design[items].replace(items_to_delete, np.nan)
    design['Blanks'] = design.isna().sum(axis=1)
    design.sort_values(['Version','Blanks'], inplace = True)
    a = design[items].values
    b = []
    for r in a:
        nulls = np.isnan(r)
        if(len(nulls) > 0):
            r = r[~nulls]
            r = np.append(r, [np.nan] * (len(items) - len(r)))
        b.append(r)
    design[items] = b
    design['Set'] = [n % design['Set'].max() + 1 for n in range (0,len(design))]
    design.drop('Blanks', axis=1, inplace=True)

    return design
 