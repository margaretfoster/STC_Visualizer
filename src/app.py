import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

## Import and manipulate data
## Base data:

## NOTES to self:
## status 6/8 is to create the dataframes I need for the data:

group_years = pd.read_csv("../data/group_years_regions.csv")
df = group_years

## Make the data for the second tab:
region_sums = group_years.groupby(["year", "region"])['delta1'].apply(lambda x:
                                                       (x == 1).sum()).reset_index(name='year_total')

numchanges = group_years.groupby(['ucdp_dset_id',
                                  'ucdp_name', 'region'])['delta1'].apply(lambda x:
                                                                (x == 1).sum()).reset_index(name='numchanges')

cols = ["ucdp_dset_id", "ucdp_name", "numchanges", "region"]
region_changes = numchanges[cols].drop_duplicates() 

## Adjust BRA which is in twice with different IDs:

region_changes.loc[(region_changes["ucdp_dset_id"] == 289), "ucdp_name" ] = "BRA1"
region_changes.loc[(region_changes["ucdp_dset_id"] == 328), "ucdp_name" ] = "BRA2"

## Some of the name are too long for the plot, make a label column with truncated names:
## Note that 21 characters is the min length to not have artificial duplicates in Europe
region_changes["label"]= [(item[:21]+"..") if 
                          len(item) > 18 else 
                          item for item in region_changes["ucdp_name"].values]



# Initialize the Dash app
app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server

app.title = "Subject to Change Viewer"

## Experimental

def description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return dbc.Card(
        id="description-card",
        children=[
            dbc.CardBody([
                #html.H5("Subject to Change Viewer"),
                html.H3("Welcome to the Subject to Change Viewer"),
                html.Div([
                    html.P(" "),
                    html.P(" "),
                    html.P("This dashboard allows you to interactively explore the data produced by Subject to Change (Foster 2024),\
                            which uses machine learning and natural language processing to estimate the existence and years of change(s) in 250+ militant organizations."), 
                    html.P("The dashboard enhances the interpretability and transparency of the model \
                           by offering a visual summary of the estimates at either the regional or individual group level. \
                           Each tab offers a different way to visualize potential change points found by the project:"),
                    html.P("1 - Yearly summary by region of operations"), 
                    html.P("2 - Tally of the change points ascribed to militant groups, presented by region"),
                    html.P("3 - Change trajectory for individual militant groups"), 
                    html.P(" "),
                    html.P(" "),
                    html.P("Interested users can access the data, replication code, and an overview of the project at: https://github.com/margaretfoster/SubjectToChange/"),
                    html.P("To use this dashboard, start by choosing the region and (where applicable) a group of interest. The lines on the plot provide years of operation between 1991-2020."),
                    html.P("Hovering over the line will provide a box that summarizes the framing for that group-year."),
                    html.P(" "),
                    html.P("Foster (2024) defines changes as group years where the line crosses the 0 (green) line, \
                            though users may choose a different threshold by creating a custom feature from the 'PropT1' and 'PropT2' columns. \
                           The substantive meaning of each end of the scale can be evaluated via the 'frexWords' column of the dataset, which is located at: \
                           (https://github.com/margaretfoster/SubjectToChange/blob/master/data/group_years_regions.csv)")
                ])
            ]),
            html.Br(),  # Add a line break for space
            html.Br(),  # Add a line break for space
        ],
    )

def plot_group(df, region1, group1):

    filtered_df = df[(df['region'] == region1) & (df['ucdp_name'] == group1)]
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
## Function for my plots:
    
def plot_region(data, region):

    df_region = data[data["region"] == region].sort_values(by="numchanges", ascending=False).drop_duplicates()
    fig = px.bar(df_region, 
                 y="label",
                 x="numchanges",
                 hover_name="ucdp_name",
                 labels={"numchanges": "Number of Associated Changes", "label": "Group Name (Abrev)" },
                 title="Change Distribution: " + region)
    fig.update_layout(plot_bgcolor='white')
    return fig


def plot_region_sum(data, region):

    region_sums = group_years.groupby(["year", "region"])['delta1'].apply(lambda x:
                                                       (x == 1).sum()).reset_index(name='year_total')
    
    plotdf = region_sums[region_sums["region"] == region]
    
    fig_rs = px.line(plotdf, 
                     x = "year", 
                     y="year_total", 
                     color="region", 
                 title="Yearly Count of Framing Changes of at Least |1|",
                labels={"year_total": "Number of Changes",
                        "year": "Year", 
                       "region": "Region"})
    fig_rs.update_layout(plot_bgcolor='white')
    return fig_rs



# App layout
app.layout = dbc.Container([
    description_card(), 
    dbc.Tabs([

        ## Tab: Region overview:

          dbc.Tab(label='Regional Overview, Time Series View', children=[
            html.Div([
                html.H4("Select Region"),
                dcc.Dropdown(
                    id='region-dropdown-time',
                    options=[{'label': r, 'value': r} for r in region_changes['region'].unique()],
                    value=region_changes['region'].unique()[0]
                ),
                dcc.Graph(id='region-time')
        ])
    ]),
        ## Tab: region summaries

        dbc.Tab(label='Regional Changes Tally, by Group', children=[
            html.Div([
                html.H4("Select Region"),
                dcc.Dropdown(
                    id='region-dropdown',
                    options=[{'label': r, 'value': r} for r in region_changes['region'].unique()],
                    value=region_changes['region'].unique()[0]
                ),
                dcc.Graph(id='region-plot')
        ])
    ]),

        ## Tab: group trajectory: 
        dbc.Tab(label='Visualize Trajectories', children=[
            html.Div([
                html.H6("Select Region"),
                dcc.Dropdown(
                    id='select-region-tab1',
                    options=[{'label': i, 'value': i} for i in df['region'].unique()],
                    value=df['region'].unique()[0],
                    placeholder="Select region"
                ),
                html.Br(),
                html.H6("Select Group"),
                dcc.Dropdown(
                    id='select-group-tab1',
                    placeholder="Select group"
                ),
                html.Br(),
                html.H6("Group Framing Trajectory (1991-2020)"),
                dcc.Graph(id='line-plot')
            ])
        ])

])
])



# Define callback to update dropdown options based on category selection
@app.callback(
    Output('select-group-tab1', 'options'),
    [Input('select-region-tab1', 'value')]
)

def update_dropdown_category2(selected_category1):
    filtered_df = df[df['region'] == selected_category1]
    options = [{'label': i, 'value': i} for i in filtered_df['ucdp_name'].unique()]
    return options

# Define callback to update line plot based on category2 selection
@app.callback(
    Output('line-plot', 'figure'),
    [Input('select-region-tab1', 'value')],
    Input('select-group-tab1', 'value')
)

def update_line_plot(selected_category1, selected_category2):
    if selected_category1 is None or selected_category2 is None:
        # Handle case when one of the categories is not selected
        return {}
    return(plot_group(df, selected_category1, selected_category2))

# Callback for group-region summary tab
@app.callback(
    Output('region-plot', 'figure'),
    [Input('region-dropdown', 'value')]
)
def update_region_plot(selected_region):
    return plot_region(region_changes, selected_region)

# Callback for time line tab
@app.callback(
    Output('region-time', 'figure'),
    [Input('region-dropdown-time', 'value')]
)
def update_region_plot(selected_region):
    return plot_region_sum(region_changes, selected_region)


# Running the app on the server
if __name__ == '__main__':
    app.run_server(debug=True)
