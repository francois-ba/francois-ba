import json
from dash import Dash, dcc, html, Input, Output, callback, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

import datasource_manager
import plotter
import geo_utils
from candidat import Candidat
from competition import Competition

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

candidat_size = 1.5

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
        lon = clickData['points'][0]['lon']
        lat = clickData['points'][0]['lat']
        candidat = Candidat(lon, lat, candidat_size).get_impacted_municipality(boundaries_geo)
        ratio_vet_pop_with_competition = Competition(veto_geo, candidat).select_direct_competitors().ratio_vet_population()
        ratio_vet_pop_without_competition = candidat.ratio_vet_population(ratio_vet_pop_with_competition)
        ratio_vet_pop  = pd.concat([ratio_vet_pop_without_competition,
                                                     ratio_vet_pop_with_competition[['weighted_ratio_vet_population','competition_area']]
                                                     ])
        avg_potential_population = ratio_vet_pop.weighted_ratio_vet_population.sum() / ratio_vet_pop.competition_area.sum()
        return [f'{int(round(avg_potential_population, 0))}']
    return ['0']

# Callback to update the zoom level display
# @app.callback(
#     Output('zoom-output', 'children'),
#     Input('controls-and-graph', 'relayoutData')
# )
# def update_zoom(relayout_data):
#     if relayout_data and 'mapbox.zoom' in relayout_data:
#         current_zoom = relayout_data['mapbox.zoom']

if __name__ == '__main__':
    app.run_server(debug=True)

