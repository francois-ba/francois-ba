import pandas as pd
import numpy as np
from scipy import stats
import geopandas as gpd

""""
Data sources
- boundaries_clean.geojson
- clinics_points.geojson
- trams_clean.geojson
- revenue.csv
- population.csv
"""

path_data = '../data/'

sel_communes = ['Mauguio', 'Castelnau-le-Lez', 'Lavérune', 'Juvignac',
                'Assas', 'Lattes', 'Saint-Gély-du-Fesc', 'Saint-Brès',
                'Montpellier', 'Mireval', 'Montferrier-sur-Lez', 'Mudaison',
                'Grabels', 'Jacou', 'Saint-Vincent-de-Barbeyrargues',
                'Prades-le-Lez', 'Castries', 'Vendargues', 'Teyran',
                'La Grande-Motte', 'Pérols', 'Saint-Clément-de-Rivière',
                'Candillargues', 'Baillargues', 'Le Crès',
                'Villeneuve-lès-Maguelone', 'Clapiers', 'Saint-Aunès', 'Guzargues',
                'Palavas-les-Flots', 'Saint-Jean-de-Védas']


def get_revenue(filename='revenue.csv'):
    df = pd.read_csv(path_data + filename)
    total_df = df[df.tranche == "Total"].iloc[:, 2:]
    total_df = total_df.replace('n.c.', np.nan).dropna(axis=0)
    total_df["revenue_avg"] = total_df.apply(
        lambda x: eval(x.revenue_reference.replace(',', '')) / eval(x.nb_foyers.replace(',', '')), axis=1)
    total_df["taxation_rate"] = total_df.apply(
        lambda x: eval(x.nb_foyers_imposes.replace(',', '')) / eval(x.nb_foyers.replace(',', '')), axis=1)
    total_df["rent_salary_ratio"] = total_df.apply(
        lambda x: eval(x.nb_foyers_retraite.replace(',', '')) / eval(x.nb_foyers_salaire.replace(',', '')), axis=1)
    total_df = total_df[['commune_name', 'nb_foyers', 'revenue_reference', 'revenue_avg', 'taxation_rate',
                         'rent_salary_ratio']]
    total_df = total_df[total_df.commune_name.isin(sel_communes)]
    return total_df


def get_population(filename='population.csv'):
    def trend_population(row):
        y = [float(row[f'p{i}_pop']) for i in range(13, 22)]
        return float(stats.linregress(x=np.linspace(13, 21, 9), y=y).slope)

    pop_df = pd.read_csv(path_data + filename)
    pop_df = pop_df[(pop_df.dep == '34') & (pop_df.libgeo.isin(sel_communes))]
    pop_df['population_trend'] = pop_df.apply(trend_population, axis=1)

    pop_df = pop_df[['libgeo', 'p21_pop', 'population_trend']].set_index('libgeo')
    assert pop_df.shape[0] == len(sel_communes)
    return pop_df

def get_boundary(revenue_df, pop_df, filename = 'boundaries_clean.geojson'):
    df_places = gpd.read_file(path_data + filename)

    data_df = df_places.merge(revenue_df[['commune_name', 'revenue_avg', 'taxation_rate', 'rent_salary_ratio']], left_on='nom_officiel_commune',
                              right_on='commune_name')

    data_df = data_df.set_index('commune_name')
    data_df = data_df.join(pop_df)
    data_df['population'] = data_df['p21_pop']
    data_df['population_log'] = data_df['population'].apply(np.log10)
    data_df['population_density'] = data_df.apply(lambda x: 1000 * x.population / eval(x.st_area_shape), axis=1)
    data_df.drop(columns=['p21_pop', 'nom_officiel_commune'], inplace=True)
    return data_df

def get_veto(filename='clinics_points.geojson'):
    veto_df = gpd.read_file(path_data + filename)
    veto_df = veto_df[veto_df.amenity == 'veterinary'][['amenity', 'name', 'effectif', 'geometry']]
    veto_df['geometry'] = veto_df.geometry.centroid
    return veto_df

def get_candidats(filename='clinic_candidats.geojson'):
    candidat_df = gpd.read_file(path_data + filename)
    return candidat_df

def get_tram(filename='trams_clean.geojson'):
    tram_df = gpd.read_file(path_data + filename)
    tram_df['lon'] = tram_df.lon.apply(lambda x: [eval(i) for i in x.split(',')])
    tram_df['lat'] = tram_df.lat.apply(lambda x: [eval(i) for i in x.split(',')])
    return tram_df

