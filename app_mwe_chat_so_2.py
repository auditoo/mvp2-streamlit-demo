# type:ignore
import hmac
import json
import time
import folium

import streamlit as st
import yaml
from openai import OpenAI
from pydantic.json_schema import models_json_schema
from pydantic import BaseModel, Field
from typing import Literal, List, Optional
import auth
from models import Description, Logement, Fenetre, Piece
from streamlit_folium import st_folium
from src.geo_ban import search_by_text, get_lat_lon
st.set_page_config(
    page_title="Auditoo",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items=None,
)



st.title("AI Diag-Assistant")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
openai_models = ["gpt-3.5-turbo", "gpt-4o-mini-2024-07-18", "gpt-4o-2024-08-06"]
openai_model = openai_models[2]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = openai_model

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Tu es un diagnostiqueur immobilier, expert dans l'analyse des logement et l'extraction de données. On va te donner de la donnée non structurée que tu vas convertir selon la structure proposée.",
        },
        {
            "role": "assistant",
            "content": "Décrivez moi le logement !",
        }
    ]

if "output_model_history" not in st.session_state:
    st.session_state.output_model_history: List[Description] = []





for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(""):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        completion = client.beta.chat.completions.parse(
            model=openai_model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            response_format=Description,
        )

        output = completion.choices[0].message.parsed
        st.session_state.output_model_history.append(output)
        json_data = output.model_dump_json(indent=2)
        response = st.write("whats next ?")



with st.sidebar:
    
    if len(st.session_state.output_model_history) > 0:
        
        d = st.session_state.output_model_history[-1]
        num = d.logement.adresse_numero
        street = d.logement.adresse_rue
        zipcode = d.logement.adresse_code_postal
        city = d.logement.adresse_ville
        
        print("adresse")
        print(num)
        print(street)
        print(zipcode)
        print(city)
        
        if num and street and (zipcode or city):
            
            q = ', '.join([str(item) for item in (num, street, zipcode, city) if item is not None])
            print(f"q = {q}")
            a = search_by_text(q, 1, type_adresse="housenumber")[0]
            print(a)
            lat, lon = get_lat_lon(a)
            
            # center on Liberty Bell, add marker
            m = folium.Map(location=[lat, lon], zoom_start=16)
            folium.Marker(
                [lat, lon], popup="Logement", tooltip="Logement"
            ).add_to(m)

            # call to render Folium map in Streamlit
            # st_data = st_folium(m, width=725)
            st_data = st_folium(center=[lat, lon], fig=m, height=200, returned_objects=[])
    
    st.divider()
    n = len(st.session_state.output_model_history)
    print(n)
    for i in range(1, n+1):
        output = st.session_state.output_model_history[-i]
        json_data = output.model_dump_json(indent=2)
        expanded = 2 if i == 1 else 0
        st.json(json_data, expanded=expanded)
        if i == 1:
            st.divider()


    
        # st.session_state.messages.append({"role": "assistant", "content": json_data})
