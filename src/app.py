import dash
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc

import datasource_manager
import plotter


# data feeding
revenue_df = datasource_manager.get_revenue()
population_df = datasource_manager.get_population()

boundaries_geo = datasource_manager.get_boundary(revenue_df.copy(), population_df)
veto_geo = datasource_manager.get_veto()
tram_coords = datasource_manager.get_tram()

#figure plotting
fig = plotter.get_fig(boundaries_geo, veto_geo, tram_coords)

# Initialize the app

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container([
    html.H1(children='MC&M Montpellier'),

    # Row container to hold radio items and graph
    dbc.Row([
        # Column for the RadioItems
        dbc.Col(
            dcc.RadioItems(
                options=[
                    {'label': 'Revenue', 'value': 'revenue'},
                    {'label': 'Taxation Rate', 'value': 'taxation_rate'},
                    {'label': 'Rent-Salary Ratio', 'value': 'rent_salary_ratio'},
                    {'label': 'Population Count', 'value': 'population_count'},
                    {'label': 'Population Density', 'value': 'population_density'},
                    {'label': 'Population Trend', 'value': 'population_trend'}
                ],
                value='revenue',
                id='controls-and-radio-item',
                inline=False  # Stack options vertically
            ),
            width=2  # Adjust width to fit your needs
        ),

        # Column for the Graph
        dbc.Col(
            dcc.Graph(id='controls-and-graph'),
            width=9  # Adjust width to ensure alignment
        )
    ], align="center")  # Vertically center the row contents
])


# Callback to update the graph based on selected metric
@callback(
    Output('controls-and-graph', 'figure'),
    Input('controls-and-radio-item', 'value')
)
def update_graph(metric):
    fig = plotter.get_fig(boundaries_geo, veto_geo, tram_coords, metric)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

