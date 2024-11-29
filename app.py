#type:ignore
import streamlit as st
import hmac
import auth
from openai import OpenAI
import models
import json
from pydantic.json_schema import models_json_schema
import yaml
import time

st.set_page_config(
    page_title="Auditoo",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items=None,
)

st.title("Auditoo - Votre compagnon Liciel")

if not auth.check_password():
    st.stop()  # Do not continue if check_password is not True.

st.header("1) Spécifiez votre description")
default_description = open("assets/default_description.md", "r").read()
description_text = st.text_area("", value=default_description, height=400)

schema = models.Description.model_json_schema()
with st.expander("Spécifications du modèle de données"):
    st.json(json.dumps(models.Description.model_json_schema(), indent=2), expanded=True)

for k, v in schema["$defs"].items():
    with st.expander(f"**{k}**"):
        st.json(json.dumps(v, indent=2), expanded=2)

st.header("2) Générer la donnée à partir de la description")

use_ai = st.toggle("Utiliser l'assitant AI ?", value=False)
b = st.button("Run")
if b:
    with st.spinner("Votre assistant analyse la description ..."):
        
        if use_ai:
            description_model = models.extract_model(description_text)
        else:
            with open('assets/default_model.json', 'r') as file:
                time.sleep(1)
                description_model = models.Description.model_validate_json(file.read())
            
        
        if description_model:
            st.success("Analyse réussie !")
            df_fenetres = {
                "piece": [],
                "largeur": [],
                "hauteur": [],
                "surface": [],
                "materiau": [],
                "type_chassis": [],
                "vitrage": [],
                "presence_grille_vmc": [],
            }
            for f in description_model.fenetres:
                f_dict = f.model_dump()
                print(f_dict)
                for k in df_fenetres.keys():
                    if k in f_dict:
                        df_fenetres[k].append(f_dict[k])
                s = round(df_fenetres["largeur"][-1] * df_fenetres["hauteur"][-1]/1e4,2)
                df_fenetres["surface"].append(s)
            st.dataframe(df_fenetres, width=None)

            json_data = description_model.model_dump_json(indent=2)
            st.json(json_data, expanded=True)
        else:
            st.error("Echec de l'analyse")
