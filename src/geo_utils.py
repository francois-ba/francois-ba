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

def inter_circle_polygon(circle:Polygon, polygon:Polygon):
    area = polygon.intersection(circle)

def influence_area_from_point(lon:float, lat:float, boundaries:DataFrame):
    center_point = Point(lon, lat)
    center_commune = boundaries[boundaries.geometry.apply(lambda x: x.contains(center_point))]
    neighbors = boundaries[boundaries.geometry.apply(lambda x: x.touches(center_commune.geometry.values[0]))]
    impacted_communes = pd.concat([center_commune, neighbors])
    #gpd.GeoDataFrame(boundaries.geometry, crs="EPSG:4326")
    circle = circle_from_point(center_point)
    impacted_communes['influence_area'] = impacted_communes.geometry.apply(lambda x: x.intersection(circle).area)
    #TODO get population