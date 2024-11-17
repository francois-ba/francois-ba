from dataclasses import dataclass

import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame
import geopandas as gpd
from shapely.geometry import Point, Polygon
from pyproj import Geod

geod = Geod(ellps="WGS84")

def km_to_degrees(lat:float, radius_km:float):
    # Compute degrees for the given radius around a latitude
    degrees, _, _ = geod.fwd(0, lat, 90, dist=radius_km * 1000)  # 90° is eastward
    return degrees

def circle_from_point(center_point:Point, radius_km=2):
    #x=lon, y=lat
    buffer_radius_deg = km_to_degrees(center_point.y, radius_km)
    return center_point.buffer(buffer_radius_deg)

def get_population_influence_area(boundary:Polygon, population: float, circle:Polygon) -> float:
    commune_area = boundary.area
    influence_area = boundary.intersection(circle).area
    ratio_area = influence_area / commune_area
    population = population * ratio_area
    return population

def population_in_polygon(polygon:Polygon, boundaries:DataFrame):
    boundaries['impacted_population'] = boundaries.apply(
        lambda x: get_population_influence_area(x.geometry, x.population, polygon), axis=1)
    return boundaries.impacted_population.sum()


# def influence_area_from_point(lon:float, lat:float, boundaries:DataFrame):
#     center_point = Point(lon, lat)
#     center_commune = boundaries[boundaries.geometry.apply(lambda x: x.contains(center_point))]
#     neighbors = boundaries[boundaries.geometry.apply(lambda x: x.touches(center_commune.geometry.values[0]))]
#     impacted_communes = pd.concat([center_commune, neighbors])
#     #gpd.GeoDataFrame(boundaries.geometry, crs="EPSG:4326") structure_size
#     circle = circle_from_point(center_point)
#     impacted_communes['impacted_population_revenue'] = impacted_communes.apply(lambda x: get_population_influence_area(x.geometry, x.population, circle), axis=1)
#     impacted_communes['impacted_population'] = impacted_communes.impacted_population_revenue.apply(lambda x:x['population'])
#     impacted_communes['impacted_ratio_area'] = impacted_communes.impacted_population_revenue.apply(lambda x:x['ratio_area'])
#     potential_population = impacted_communes.impacted_population.sum()
#     #potential_avg_revenue = impacted_communes.revenue_avg.sum() / impacted_communes.impacted_ratio_area.sum()
#     return potential_population
#
# def get_competition_polygon(competitor_area:Polygon, candidat_area:Polygon):
#     pass
#
# def competition_from_point(lon:float, lat:float, vetos:DataFrame, candidat_size):
#     center_point = Point(lon, lat)
#     candidat_circle = circle_from_point(center_point)
#     vetos['competition_circle'] = vetos.geometry.apply(lambda x: circle_from_point(x))
#     vetos['competition_polygon'] = vetos.apply(lambda x: get_competition_polygon(x.competition_circle,candidat_circle),axis=1)
#     vetos['competition_population'] = vetos.competition_polygon.apply(lambda x: x.get_population_influence_area, )



