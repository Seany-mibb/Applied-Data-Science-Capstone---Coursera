# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            *[{'label': site, 'value': site} for site in spacex_df["Launch Site"].unique()]
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    html.Br(),

    # Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # Payload slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        value=[3000, 6000]
    ),

    # Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(input_site):
    if input_site == "ALL":
        filtered_df = spacex_df[spacex_df['class'] == 1]
        df_counts = filtered_df['Launch Site'].value_counts().reset_index()
        df_counts.columns = ['Launch Site', 'Successes']
        fig = px.pie(
            df_counts,
            values='Successes',
            names='Launch Site',
            title='Total Success Launches by Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == input_site]
        df_counts = filtered_df['class'].value_counts().reset_index()
        df_counts.columns = ['class', 'count']

        # Ensure both 0 and 1 appear even if one is missing
        if 0 not in df_counts['class'].values:
            df_counts = pd.concat([df_counts, pd.DataFrame({'class': [0], 'count': [0]})])
        if 1 not in df_counts['class'].values:
            df_counts = pd.concat([df_counts, pd.DataFrame({'class': [1], 'count': [0]})])
        df_counts = df_counts.sort_values(by='class')

        fig = px.pie(
            df_counts,
            values='count',
            names='class',
            title=f'Success vs Failed Launches for {input_site}',
            color='class',
            color_discrete_map={0: 'red', 1: 'green'}
        )
        fig.update_traces(textinfo='percent+label')

    return fig


# Callback for scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('payload-slider', 'value'),
     Input('site-dropdown', 'value')]
)
def get_scatter_plot(input_range, input_site):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= input_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= input_range[1])
    ]

    if input_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == input_site]
        title = f'Payload vs Success for {input_site}'
    else:
        title = 'Payload vs Success for All Sites'

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version',
        title=title,
        labels={'class': 'Launch Outcome (0=Failure, 1=Success)'}
    )

    return fig


# Run the app
if __name__ == '__main__':
    app.run()
