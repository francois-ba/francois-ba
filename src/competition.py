from dataclasses import dataclass
import pandas as pd

import geo_utils
from shapely.geometry import Point, Polygon

from src.candidat import Candidat


@dataclass()
class Competition:
    competitors: pd.DataFrame
    candidat: Candidat

    def __post_init__(self):
        self.competitors['competition_circle'] = self.competitors.geometry.apply(lambda x: geo_utils.circle_from_point(x))
        return self

    def select_direct_competitors(self):
        self.competitors['competition_polygon'] = self.competitors.competition_circle.apply(lambda x: x.intersection(self.candidat.circle))
        self.competitors['competition_area'] = self.competitors.competition_polygon.apply(lambda x: x.area)
        self.competitors = self.competitors[self.competitors.competition_area > 0]
        return self

    def ratio_vet_population(self):
        self.competitors['population'] = self.competitors.competition_polygon.apply(lambda x: geo_utils.population_in_polygon(x, self.candidat.impacted_communes))
        self.competitors['effectif'] = self.competitors.effectif.apply(lambda x: eval(x) if x is not None else 2)
        self.competitors['ratio_vet_population'] = self.competitors.apply(lambda x: x.population / (x.effectif + self.candidat.size), axis=1)
        self.competitors['weighted_ratio_vet_population'] = self.competitors.apply(lambda x:x.ratio_vet_population * x.competition_area, axis=1)
        return self.competitors





