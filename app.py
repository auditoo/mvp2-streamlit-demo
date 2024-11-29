import streamlit as st
import hmac
import auth
from openai import OpenAI
import models
import json
from pydantic.json_schema import models_json_schema
import yaml


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
defaut_text = open("assets/text.md", "r").read()
description_text = st.text_area("", value=defaut_text, height=400)

schema = models.Description.model_json_schema()
with st.expander("Spécifications du modèle de données"):
    st.json(json.dumps(models.Description.model_json_schema(), indent=2), expanded=True)
    
for k,v in schema["$defs"].items():
    with st.expander(f"**{k}**"):
        st.json(json.dumps(v, indent=2), expanded=2)

    

st.header("2) Générer la donnée à partir de la description")
b = st.button("Run")
if b:
    with st.spinner("Votre assistant analyse la description ..."):
        description_model = models.extract_model(description_text)
        if description_model:
            st.success("Analyse réussie !")
            json_data = description_model.model_dump_json(indent=2)
            st.json(json_data, expanded=True)
        else:
            st.error("Echec de l'analyse")
            
