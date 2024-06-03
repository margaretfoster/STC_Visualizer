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
group_years = pd.read_csv("../data/group_years_regions.csv")


# Sample data
df=group_years

# Initialize the Dash app
app = dash.Dash(__name__)

app.title = "Subject to Change Viewer"

## Experimental

def description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Subject to Change Viewer"),
            html.H3("Welcome to the Subject to Change Viewer"),
            html.Div(
                id="intro",
                children= [
                    html.P("This dashboard allows you to explore how Subject to Change (Foster 2024) characterizes change in militant groups by focusing on the trajectories of specific groups."), 
                    html.P("An aggregate summary can be viewed on the accompanying project page, at: PLACEHOLDER FOR FINAL URL"),
                    html.P(" "),
                    html.P("To use this dashboard, start by chosing the region, and then a group of interest. The lines on the plot provide years of operation between 1991-2020."),
                    html.P("Hovering over the line will provide a box that summarizes the framing for that group-year."),
                    html.P(" "),
                    html.P("Foster (2024) defines changes as group years where the line crosses the 0 (green) line, \
                            though users may choose a different threshold by creating a custom feature from the 'PropT1' and 'PropT2' columns.")
                ]
            ),
            html.Br(),  # Add a line break for space
            html.Br(),  # Add a line break for space
        ],
    )


# App layout
app.layout = html.Div([
    description_card(), 
    html.H6("Select Region"),
    dcc.Dropdown(
        id='dropdown-category1',
        options=[{'label': i, 'value': i} for i in df['region'].unique()],
        value=df['region'].unique()[0],
        placeholder="Select region"
    ),
    html.Br(),
    html.H6("Select Group"),
    dcc.Dropdown(
        id='dropdown-category2',
        placeholder="Select group"
    ),
    html.Br(),
    html.H6("Group Framing Trajectory (1991-2020)"),
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

#Running the app on the server
server = app.server

## Run:
if __name__ == '__main__':
    app.run(debug=True)
