from typing import List, Literal
from pydantic import BaseModel, Field
from openai import OpenAI

PeriodeConstruction = Literal[
    "avant 1948",
    "1948-1974",
    "1975-1977",
    "1978-1982",
    "1983-1988",
    "1989-2000",
    "2001-2005",
    "2006-2012",
    "2013-2021",
    "après 2021",
]


class Logement(BaseModel):
    type_batiment: Literal["maison", "appartement"] = Field(
        title="type de bâtiment",
        default="appartement",
    )
    surface: float | None = Field(
        title="surface habitable du logement en mètres carrés",
    )
    hsp: float | None = Field(
        title="hauteur sous plafond du logement en mètres",
    )
    annee_construction: int | None = Field(
        title="année de construction du logement",
    )
    periode_construction: PeriodeConstruction | None = Field(
        title="la période de construction du logement",
    )
    nbr_niveaux: int = Field(
        title="nombre de niveaux du logement",
    )
    adresse_numero: str = Field(
        title="numéro de rue de l'adresse du bâtiment",
    )
    adresse_rue: str = Field(
        title="nom de rue de l'adresse du bâtiment",
    )
    adresse_code_postal: str = Field(
        title="code postal de l'adresse du bâtiment",
    )
    adresse_ville: str = Field(
        title="nom de la ville de l'adresse du bâtiment",
    )


class Fenetre(BaseModel):
    largeur: float = Field(
        title="largeur de la fenêtre en centimètres",
    )
    hauteur: float = Field(
        title="hauteur de la fenêtre en centimètres",
    )
    hauteur_allege: float | None = Field(
        title="hauteur de l'allège de la fenêtre",
        # default=80.0
    )
    piece: str = Field(
        title="pièce dans laquelle est située la fenêtre",
    )
    materiau: Literal["bois", "pvc", "aluminium", "acier", "composite"] = Field(
        title="le matériau dans lequel est réalisée la fenêtre", default="pvc"
    )
    position: Literal["tunnel", "nu-intérieur", "nu-extérieur"] = Field(
        title="le type de pose de la fenêtre sur le bâti", default="tunnel"
    )
    type_chassis: Literal[
        "fixe", "à vantaux", "coulissant", "bascullant", "oscillo-battant"
    ] = Field(title="le type de chassis de la fenêtre", default="à vantaux")
    nbr_vantaux: int | None = Field(
        title="le nombre de ventaux de la fenêtre", default=None
    )
    vitrage: Literal[
        "simple-vitrage", "sur-vitrage", "double-vitrage", "triple-vitrage"
    ] = Field(title="le type de vitrage de la fenêtre", default="double-vitrage")
    vitrage_epaisseur_lame_air: int | None = Field(
        title="l'épaisseur de la lame d'air en milimètre si la fenêtre est en double vitrage.",
        default=None,
    )
    presence_grille_vmc: bool = Field(
        title="presence d'une grille d'entrée d'air pour la VMC",
        description="indique si la menuiserie comporte une grille d'entrée d'air pour la VMC.",
        # default=False
    )


class Description(BaseModel):
    logement: Logement
    fenetres: List[Fenetre]


client = OpenAI()


def extract_model(content: str) -> Description | None:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": "Tu es un diagnostiqueur immobilier, expert dans l'analyse des logement et l'extratction de données. On va te donner de la donnée non structurée, que tu vas convertir selon la structure proposée.",
            },
            {
                "role": "user",
                "content": content,
            },
        ],
        response_format=Description,
    )

    description = completion.choices[0].message.parsed
    return description
    # if description:
    #     ts = '{:%Y-%m-%d_%H-%M-%S}'.format(datetime.datetime.now())
    #     with open(f"description_{ts}.json", "w") as f:
    #         data = description.model_dump_json(indent=2)
    #         f.write(data)
    #         print(data)
    #         return description
