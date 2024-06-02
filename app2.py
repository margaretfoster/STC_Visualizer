import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import sys

# Check your Python executable path
print(sys.executable)

## Import and manipulate data
group_years = pd.read_csv("./data/group_years_regions.csv")


# Sample data
df=group_years

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    dcc.Dropdown(
        id='dropdown-category1',
        options=[{'label': i, 'value': i} for i in df['region'].unique()],
        value=df['region'].unique()[0]
    ),
    html.Br(),
    dcc.Dropdown(id='dropdown-category2'),
    html.Br(),
    dcc.Graph(id='line-plot')
])

# Define callback to update dropdown options based on category1 selection
@app.callback(
    Output('dropdown-category2', 'options'),
    [Input('dropdown-category1', 'value')]
)
def update_dropdown_category2(selected_category1):
    filtered_df = df[df['region'] == selected_category1]
    options = [{'label': i, 'value': i} for i in filtered_df['ucdp_name'].unique()]
    return options

# Define callback to update line plot based on category2 selection
@app.callback(
    Output('line-plot', 'figure'),
    [Input('dropdown-category1', 'value'),
     Input('dropdown-category2', 'value')]
)
def update_line_plot(selected_category1, selected_category2):
    filtered_df = df[(df['region'] == selected_category1) & (df['ucdp_name'] == selected_category2)]
    filtered_df = filtered_df.sort_values(by="year") ## filter for line sanity, new line for readiability
    
    fig = px.line(filtered_df, 
                     x="year", 
                     y="propdiff", 
                  color="ucdp_name", 
                 labels={
                     "propdiff": "Frame Summary",
                     "udcp_name": "Group Name",
                     "year": "Year", 
                     'ucdp_name' : "Selected Group"
                 })
    fig.update_xaxes(range=[1991, 2020])
    fig.add_hline(y=0.0, line_dash="dash", line_color="green")
    fig.update_layout(yaxis_range=[-1,1],  
                      xaxis={'dtick': 1},
                      
                     )
    fig.update_layout(plot_bgcolor='white')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

