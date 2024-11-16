import json
import plotly.express as px
import plotly.graph_objects as go



def get_fig(boundary_layer, veto_layer, candidat_layer, tram_layer, metric="revenue"):
    metric_mapping = {
        'revenue': {'color':'revenue_avg',
                    'hover_data': 'revenue_avg'},
        'taxation_rate': {'color':'taxation_rate',
                    'hover_data': 'taxation_rate'},
        'rent_salary_ratio': {'color': 'rent_salary_ratio',
                             'hover_data': 'rent_salary_ratio'},
        'population_count': {'color':'population_log',
                    'hover_data': 'population'},
        'population_density': {'color': 'population_density',
                             'hover_data': 'population_density'},
        'population_trend': {'color': 'population_trend',
                               'hover_data': 'population_trend'},
    }

    geojson_data = json.loads(boundary_layer.to_json())
    fig = px.choropleth_mapbox(
        data_frame=boundary_layer,
        geojson=geojson_data,
        locations="nom_commune_utf8",
        featureidkey="properties.nom_commune_utf8",
        color=metric_mapping[metric]['color'],
        hover_data = metric_mapping[metric]['hover_data'],
        opacity = 0.6,
        title = metric
    )

    fig.add_trace(go.Scattermapbox(
        lon=veto_layer.geometry.x,
        lat=veto_layer.geometry.y,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color='blue'
        ),
        text=veto_layer['name'],
        name='veto',
        showlegend=False
    ))

    fig.add_trace(go.Scattermapbox(
        lon=candidat_layer.geometry.x,
        lat=candidat_layer.geometry.y,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color='orange'
        ),
        text=candidat_layer['name'],
        name='Mon chat et moi',
        showlegend=False
    ))

    for _, row in tram_layer.iterrows():
        fig.add_trace(go.Scattermapbox(
            lon=list(row['lon']),
            lat=list(row['lat']),
            mode="lines",
            line=dict(width=3, color="green"),
            name='tramways',
            showlegend=False
        ))

    fig.update_layout(
        uirevision="constant",
        mapbox=dict(
            style="carto-positron",
            zoom=11,
            center={"lat": 43.64, "lon": 3.95},
        ),
        width = 1260,
        height = 860,
        margin={"r":2,"t":2,"l":2,"b":2},
        paper_bgcolor='#303030',  # Dark grey background for the figure area
        font_color='white'
    )
    return fig