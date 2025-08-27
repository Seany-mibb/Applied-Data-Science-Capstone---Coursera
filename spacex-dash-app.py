# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
print(spacex_df["Launch Site"].unique()[0])
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': f'{spacex_df["Launch Site"].unique()[0]}', 'value': f'{spacex_df["Launch Site"].unique()[0]}'},
                                        {'label': f'{spacex_df["Launch Site"].unique()[1]}', 'value': f'{spacex_df["Launch Site"].unique()[1]}'},
                                        {'label': f'{spacex_df["Launch Site"].unique()[2]}', 'value': f'{spacex_df["Launch Site"].unique()[2]}'},
                                        {'label': f'{spacex_df["Launch Site"].unique()[3]}', 'value': f'{spacex_df["Launch Site"].unique()[3]}'},
                                    ],
                                    value = "ALL",
                                    placeholder = "Place holder here",
                                    searchable = True
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                value=[3000, 6000]

                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
            Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(input_site):
    if input_site == "ALL":
        filtered_df = spacex_df[spacex_df['class'] == 1]
        values = filtered_df['Launch Site'].value_counts().values
        names = filtered_df['Launch Site'].value_counts().index
        title = 'Total Success Launches by Site'
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == input_site]
        values = filtered_df['class'].value_counts().values
        names = filtered_df['class'].value_counts().index
        title = f'Success vs Failed Launches for {input_site}'
    
    fig = px.pie(values=values, names=names, title=title)
    
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
            Input(component_id='payload-slider', component_property='value'),
            Input(component_id='site-dropdown', component_property='value'))
def get_scatter_plot(input_range, input_site):
    # Filtering the payload mass first
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= input_range[0]) &
                            (spacex_df['Payload Mass (kg)'] <= input_range[1])
    ]

    if input_site == 'ALL':
        title = 'Payload vs Success for All Sites'
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == input_site]
        title = f'Payload vs Success for {input_site}'
    
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version',
        title=title,
        labels={'class': 'Launch Outcome (0 Failure, 1 Success)'}
    )

    return fig
# Run the app
if __name__ == '__main__':
    app.run()
