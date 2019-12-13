import plotly
import pandas as pd, numpy as np
import json
import plotly.graph_objs as go
import plotly.express as px

def create_plot():

    N = 40
    x = np.linspace(0, 1, N)
    y = np.random.randn(N)
    df = pd.DataFrame({'x': x, 'y': y}) # creating a sample dataframe

    ##bar chart
    # data = [
    #     go.Bar(
    #         x=df['x'], # assign x as the dataframe column 'x'
    #         y=df['y']
    #     )
    # ]

    ## single violin
    # tips = px.data.tips()
    # data = px.violin(tips, y="total_bill", box=True, # draw box plot inside the violin
    #             points='all', # can be 'outliers', or False
    #            )

    # multiple violins
    tips = px.data.tips()
    data = px.violin(tips, y="tip", x="smoker", color="sex", box=True, points="all",
          hover_data=tips.columns)

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON