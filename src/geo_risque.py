
from http import HTTPStatus

import requests
from src.geo_ban import get_lat_lon, search_by_text


def get_rapport_risque(latitude:float, longitude:str) -> dict:
    url = "https://georisques.gouv.fr/api/v1/resultats_rapport_risque"
    params = {"latlon": f"{longitude},{latitude}"}

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

    
if __name__ == "__main__":

    q = "2, rue du moulin, 26400, allex"
    a = search_by_text(q, 1, type_adresse="housenumber")[0]
    lat, lon = get_lat_lon(a)
    print(f"http://maps.google.com/?q={lat},{lon}")
    
    risk_report = get_rapport_risque(lat, lon)
    
    pass
