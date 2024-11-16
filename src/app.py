import json
from dash import Dash, dcc, html, Input, Output, callback, State, dash_table
import dash_bootstrap_components as dbc

import datasource_manager
import plotter
import geo_utils

# data feeding
revenue_df = datasource_manager.get_revenue()
population_df = datasource_manager.get_population()

boundaries_geo = datasource_manager.get_boundary(revenue_df.copy(), population_df)
veto_geo = datasource_manager.get_veto()
candidats = datasource_manager.get_candidats()
tram_coords = datasource_manager.get_tram()

center={"lat": 43.64, "lon": 3.95}
init_zoom = 11
current_zoom = init_zoom

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
            width=2
        ),

        # Column for the Graph
        dbc.Col(
            dcc.Graph(id='controls-and-graph'), width=9)
    ],
        align="center")
])


# Callback to update the graph based on selected metric
@callback(
    Output('controls-and-graph', 'figure'),
    Input('controls-and-radio-item', 'value')
)
def update_graph(metric):
    fig = plotter.get_fig(boundaries_geo, veto_geo, candidats, tram_coords, metric)
    return fig

@app.callback(
    [Output('textarea_coordinates', 'value')],
    Input('controls-and-graph', 'clickData'),
    #State('textarea_coordinates', 'value')
)
def display_click_data(clickData):
    if clickData is not None:
        #print(current_zoom)
        lon = clickData['points'][0]['lon']
        lat = clickData['points'][0]['lat']
        geo_utils.influence_area_from_point(lon, lat, boundaries_geo)

        #x = (clickData['points'][0]['bbox']['x0']+clickData['points'][0]['bbox']['y1']) / 2
        #y = (clickData['points'][0]['bbox']['y0'] + clickData['points'][0]['bbox']['y1']) / 2
    #     if lon is not None and lat is not None:
    #         return [','.join([str(round(i, 5)) for i in [lon,lat]])]
    return ['0, 0']

# Callback to update the zoom level display
@app.callback(
    Output('zoom-output', 'children'),
    Input('controls-and-graph', 'relayoutData')
)
def update_zoom(relayout_data):
    if relayout_data and 'mapbox.zoom' in relayout_data:
        current_zoom = relayout_data['mapbox.zoom']

if __name__ == '__main__':
    app.run_server(debug=True)

