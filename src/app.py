import json
import dash
from dash import Dash, dcc, html, Input, Output, callback, State, dash_table
import dash_bootstrap_components as dbc

import datasource_manager
import plotter


# data feeding
revenue_df = datasource_manager.get_revenue()
population_df = datasource_manager.get_population()

boundaries_geo = datasource_manager.get_boundary(revenue_df.copy(), population_df)
veto_geo = datasource_manager.get_veto()
tram_coords = datasource_manager.get_tram()

center={"lat": 43.64, "lon": 3.95}
zoom = 11

#figure plotting
#fig = plotter.get_fig(boundaries_geo, veto_geo, tram_coords)

# Initialize the app

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container([
    html.H1(children='MC&M Montpellier'),

    # Row container to hold radio items and graph
    dbc.Row([
        # Column for the RadioItems
        dbc.Col(
        html.Div(
            [dcc.RadioItems(
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
                dcc.Textarea(
                        id='textarea_coordinates',
                        value='Textarea',
                        style={'width': '100%', 'height': 32}
                ),
                html.Div(id='zoom-output')
                #dcc.Store(id='coordinates_id')
                ]
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

@app.callback(
    Output('textarea_coordinates', 'value'),
    Input('controls-and-graph', 'clickData'),
    #State('textarea_coordinates', 'value')
)
def display_click_data(clickData):
    if clickData is not None:
        return str(round(clickData['points'][0]['bbox']['x0'], 5))

# Callback to update the zoom level display
@app.callback(
    Output('zoom-output', 'children'),
    Input('controls-and-graph', 'relayoutData')
)
def update_zoom(relayout_data):
    if relayout_data and 'mapbox.zoom' in relayout_data:
        zoom_level = relayout_data['mapbox.zoom']
        return f"Current Zoom Level: {zoom_level:.2f}"
    return "Zoom Level: Not available"

# @callback(Output('coordinates_id', 'children'),
#               [Input('controls-and-graph', 'clickData')])
# def click_coord(e):
#     if e is not None:
#         return json.dumps(e)
#     else:
#         return "-"

if __name__ == '__main__':
    app.run_server(debug=True)

