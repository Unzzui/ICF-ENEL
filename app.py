from csv import writer
from datetime import date
from matplotlib.pyplot import text
import streamlit as st
import pandas as pd
import numpy as np
from re import sub
from PIL import Image
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import plotly_express as px
from charts.i_inmb import i_inmb
from charts.i_obras import i_obras
from charts.i_seg import i_seg
from charts.i_med import i_med


# ---- Start App ----- 

img_e_enel = Image.open("images/e_enel.png")
img_oca = Image.open("images/oca.jpg")
img_enel = Image.open("images/enel.png")
img_enel_oca = Image.open("images/enel_oca.png")
#  ---- Web App Title ----

st.set_page_config(page_title="Informes de Calidad Florida", page_icon= img_e_enel, layout="wide")

st.markdown(("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""),unsafe_allow_html=True)

st.image(img_enel_oca, width=400)


report = st.sidebar.selectbox(
    "Seleccione el informe",
    options=("Informe Calidad de Obras", "Informe de Seguridad", "Informe de Medio Ambiente"),

    )

# if report == "Informe Calidad Inmobiliaria": 
#     i_inmb()
    
if report == "Informe Calidad de Obras":
    i_obras()
   
elif report == "Informe de Seguridad":
    i_seg()
    
elif report == "Informe de Medio Ambiente":
    i_med()    
   