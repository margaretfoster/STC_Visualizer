
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

app = Dash(__name__)

## Import and manipulate data
group_years = pd.read_csv("./data/group_years_regions.csv")
unq = group_years.ucdp_name.unique().tolist()

## Identify which plot:
tst_asia = group_years[group_years["region"] == "Asia"].ucdp_name.unique().tolist()


app = Dash(__name__)


app.layout = html.Div([
    html.H4('Groups in Asia'),
    dcc.Graph(id="graph"),
    dcc.Dropdown(
        id="dropdown",
        options = tst_asia,
        value=[tst_asia[0]],
        #inline=True
    ),
])


@app.callback(
    Output("graph", "figure"), 
    Input("dropdown", "value"))

def update_line_chart(value):
  
    df = group_years[group_years["region"] == "Asia"].sort_values(by="year") # replace with your own data source
    mask = df.ucdp_name.isin([value])
    
    fig = px.line(df[mask], 
                     x="year", 
                     y="propdiff", 
                  color="ucdp_name", 
                 labels={
                     "propdiff": "Frame Summary",
                     "udcp_name": "Group Name",
                     "year": "Year"
                 })
    fig.add_hline(y=0.0, line_dash="dash", line_color="green")
    fig.update_layout(yaxis_range=[-1,1])
    fig.update_layout(plot_bgcolor='white')
    fig.update_layout(showlegend=False) 
    return fig


app.run_server(debug=True)