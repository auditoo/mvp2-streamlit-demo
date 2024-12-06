"""
Routines pour l'utilisation de l'API de la base adresse nationale (BAN).
"""

import requests
from http import HTTPStatus
from typing import List, Literal, Tuple
from typing_extensions import get_args
from lambert import Lambert93, convertToWGS84Deg


TypeAdresse = Literal["housenumber", "street", "locality", "municipality"]


def search_by_text(
    search_text: str, limit: int = 5, **kwargs: str | TypeAdresse
) -> List[dict]:
    """_summary_

    Args:
        search_text (str): Texte de recherche.
        limit (int, optional): Nombre maximum de résultats retournés. Defaults to 5.

        type_adresse (TypeAdresse) : Filtrer par type d'adresse ("housenumber", "street", "locality", "municipality").
        code_insee (str) : Filtrer par le code insee de la commune.
        code_postal (str) : Filtrer par code postal.
        latitude (float) : Priorité via longitude.
        longitude (float) : Priorité via latitude.

    Returns:
        List[dict]: _description_
    """
    url = "https://api-adresse.data.gouv.fr/search"
    params = {"q": search_text, "limit": limit, "autocomplete": 0}

    if "type_adresse" in kwargs:
        if kwargs["type_adresse"] in get_args(TypeAdresse):
            params["type"] = kwargs["type_adresse"]
    if "code_insee" in kwargs:
        params["citycode"] = kwargs["code_insee"]
    if "code_postal" in kwargs:
        params["postcode"] = kwargs["code_postal"]
    if "latitude" in kwargs:
        params["lat"] = kwargs["latitude"]
    if "longitude" in kwargs:
        params["lon"] = kwargs["longitude"]

    response = requests.get(url, params=params)

    if response.status_code == HTTPStatus.OK:
        results = response.json()
        return list(map(lambda f: f["properties"], results["features"]))
    else:
        print(response)
        pass

    return []


def get_lat_lon(ban_address:dict) -> Tuple[float, float]:
    x = ban_address["x"]
    y = ban_address["y"]
    pt = convertToWGS84Deg(x, y, Lambert93)
    lat = pt.getY()
    lon = pt.getX()
    return (lat, lon)


if __name__ == "__main__":

    q = "2, rue du moulin, 26400, allex"
    a = search_by_text(q, 1, type_adresse="housenumber")[0]
    lat, lon = get_lat_lon(a)
    print(f"http://maps.google.com/?q={lat},{lon}")
    pass
