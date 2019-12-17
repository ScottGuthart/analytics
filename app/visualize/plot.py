import plotly
import pandas as pd, numpy as np
import json
import plotly.graph_objs as go
import plotly.express as px

def create_plot(df, x, y, color):

    # multiple violins
    tips = df
    if x == "NONE":
          x = None
    if color == "NONE":
          color = None

    data = px.violin(tips, y=y, x=x, color=color, box=True, points="all",
          hover_data=tips.columns)

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON