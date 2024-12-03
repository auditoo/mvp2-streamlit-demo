# type:ignore
import hmac
import json
import time

import streamlit as st
import yaml
from openai import OpenAI
from pydantic.json_schema import models_json_schema
from pydantic import BaseModel, Field
from typing import Literal, List, Optional
import auth
import models

st.set_page_config(
    page_title="Auditoo",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items=None,
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


st.title("AI Diag-Assistant")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
openai_models = ["gpt-3.5-turbo", "gpt-4o-2024-08-06"]
openai_model = openai_models[1]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = openai_model

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Tu es un diagnostiqueur immobilier, expert dans l'analyse des logement et l'extratction de données. On va te donner de la donnée non structurée, que tu vas convertir selon la structure proposée.",
        },
        {
            "role": "assistant",
            "content": "Décrivez moi la fenêtre !",
        }
    ]

if "output_model_history" not in st.session_state:
    st.session_state.output_model_history: List[Fenetre] = []

for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(""):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # stream = client.chat.completions.create(
        #     model=st.session_state["openai_model"],
        #     messages=[
        #         {"role": m["role"], "content": m["content"]}
        #         for m in st.session_state.messages
        #     ],
        #     stream=True,
        # )
        # response = st.write_stream(stream)

        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            response_format=Fenetre,
        )

        output = completion.choices[0].message.parsed
        st.session_state.output_model_history.append(output)
        json_data = output.model_dump_json(indent=2)
        # response = st.write(json_data)
        print(json_data)
        
    with st.sidebar:
        n = len(st.session_state.output_model_history)
        print(n)
        for i in range(1, n+1):
            output = st.session_state.output_model_history[-i]
            json_data = output.model_dump_json(indent=2)
            expanded = 2 if i == 1 else 0
            st.json(json_data, expanded=expanded)

        # st.session_state.messages.append({"role": "assistant", "content": json_data})
