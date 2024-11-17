from dataclasses import dataclass
import pandas as pd

import geo_utils
from shapely.geometry import Point, Polygon

@dataclass()
class Candidat:
    lon:float
    lat:float
    size: float

    def __post_init__(self):
        self.center_point = Point(self.lon, self.lat)
        self.circle = geo_utils.circle_from_point(self.center_point)
        return self

    def get_impacted_municipality(self, boundaries):
        #variant: checking all intersections of circle with all boundaries (slower but more exact)
        center_commune = boundaries[boundaries.geometry.apply(lambda x: x.contains(self.center_point))]
        neighbors = boundaries[boundaries.geometry.apply(lambda x: x.touches(center_commune.geometry.values[0]))]
        self.impacted_communes = pd.concat([center_commune, neighbors])
        self.impacted_communes['unit_area'] = self.impacted_communes.geometry.apply(lambda x: x.area)
        return self

    def ratio_vet_population(self, competitors: pd.DataFrame) -> pd.DataFrame:
        competition_areas = competitors.competition_polygon.values
        for polygon in competition_areas:
            self.circle = self.circle.difference(polygon)
        area_without_competition = self.circle.area
        population_without_competition = geo_utils.population_in_polygon(self.circle, self.impacted_communes)
        ratio_vet_population = population_without_competition / self.size
        weighted_ratio_vet_population = ratio_vet_population * area_without_competition
        return pd.DataFrame([{'weighted_ratio_vet_population': weighted_ratio_vet_population , 'competition_area': area_without_competition}])
