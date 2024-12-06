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
from src.geo_risque import get_rapport_risque
openai_models = ["gpt-3.5-turbo", "gpt-4o-mini-2024-07-18", "gpt-4o-2024-08-06"]
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
openai_model = openai_models[2]

st.set_page_config(
    
    page_title="Auditoo",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None,
)

def init():
    
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

    if "ban_result" not in st.session_state:
        st.session_state.ban_result = None
    
    if "widget_map_enable" not in st.session_state:
        st.session_state.widget_map_enable = False
        
    if "risk_report" not in st.session_state:
        st.session_state.risk_report = None
    
    if "widget_risk_enable" not in st.session_state:
        st.session_state.widget_risk_enable = False


def widget_map():
    
    st.session_state.widget_map_enable = False
        
    d = st.session_state.output_model_history[-1]
    num = d.logement.adresse_numero
    street = d.logement.adresse_rue
    zipcode = d.logement.adresse_code_postal
    city = d.logement.adresse_ville
    
    if num and street and (zipcode or city):
                            
            q = ', '.join([str(item) for item in (num, street, zipcode, city) if item is not None])
            print(f"q = {q}")
            a = search_by_text(q, 1, type_adresse="housenumber")[0]
            print(a)
            lat, lon = get_lat_lon(a)
            
            st.session_state.ban_result = a
            st.session_state.widget_map_enable = True
            
            with st.expander(f"Localisation : {a["label"]}", expanded=True):

                # center on Liberty Bell, add marker
                m = folium.Map(location=[lat, lon], zoom_start=16)
                folium.Marker(
                    [lat, lon], popup="Logement", tooltip="Logement"
                ).add_to(m)

                # call to render Folium map in Streamlit
                # st_data = st_folium(m, width=725)
                st_data = st_folium(m, height=300)

def widget_risks():
        
    print("--- widget_risks ---")
    print(f"st.session_state.ban_result = {st.session_state.ban_result is None}")
    print(f"st.session_state.risk_report = {st.session_state.risk_report is None}")
    
    if st.session_state.ban_result is not None:
        if st.session_state.risk_report is None:
            lat, lon = get_lat_lon(st.session_state.ban_result)
            with st.spinner("Génération de l'état des risques ..."):
                st.session_state.risk_report = get_rapport_risque(lat, lon)  # noqa: F821
        
    print(f"st.session_state.ban_result = {st.session_state.ban_result is None}")
    print(f"st.session_state.risk_report = {st.session_state.risk_report is None}")
    
    if st.session_state.risk_report is not None:
        risk_report = st.session_state.risk_report
        for risk_type in ("Naturels", "Technologiques"):
            if risk_type == "Naturels":
                warn_icon = "⚠️"
            else:
                warn_icon = "☢️"
                
            risk_on = []
            risk_off = []
            for k, v in risk_report[f"risques{risk_type}"].items():
                tag = v["libelle"]
                if v["present"]:
                    risk_on.append(f"{warn_icon} {tag}")
                else:
                    risk_off.append(f"🆗 {tag}")
            
            report_link = f"[rapport détaillé]({risk_report['url']})"
            with st.expander(f"Etat des risques **{risk_type}** ({len(risk_on)}/{len(risk_on)+len(risk_off)}", expanded=False):
                st.divider()
                st.caption(report_link)
                
                st.markdown('\n\n'.join(risk_on))
                # st.divider()
                st.markdown("\n\n".join(risk_off))
                st.divider()
                st.json(risk_report[f"risques{risk_type}"], expanded=False)
        
def widget_pieces():
    
    if len(st.session_state.output_model_history) > 0:
        d:Description = st.session_state.output_model_history[-1]
        with st.expander("Listing des pièces"):
            st.json(d.pieces)
                   

init()


st.title("Diag Buddy")
st.caption("Votre assitant AI sur le terrain pour des diagnostiques immobiliers précis et fiables.")

c1, c2, c3 = st.columns((1, 1, 1), gap="large")
prompt = st.chat_input("décrivez moi le logement ...")

with c1:

    st.subheader("Discussion")

    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt:
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
            # response = st.write("whats next ?")


with c2:
    
    st.subheader("Widgets")
    
    if len(st.session_state.output_model_history) > 0:
        
        widget_map()
        widget_risks()
        widget_pieces()
    
with c3:
    
    st.subheader("Data Model")
    n = len(st.session_state.output_model_history)
    
    
    if n > 0:
        
        st.caption("Dernière version")
        output = st.session_state.output_model_history[-1]
        json_data = output.model_dump_json(indent=2)
        st.json(json_data, expanded=2)
        
        st.divider()
        st.caption("Historique")
        
        for i in range(2, n+1):
            output = st.session_state.output_model_history[-i]
            json_data = output.model_dump_json(indent=2)
            st.json(json_data, expanded=False)
                


    
        # st.session_state.messages.append({"role": "assistant", "content": json_data})
