from csv import writer
from datetime import date
from operator import index
from matplotlib.pyplot import text, title
from scipy.fftpack import ss_diff
import streamlit as st
import pandas as pd
import numpy as np
from re import S, sub
from PIL import Image
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import plotly_express as px



def i_med():
    # ----- Start -----
    st.markdown("""
    
    # Dashboard Resumen Medio Ambiente
    
    """)
    
    # ---- Function ----
    
    @st.cache(ttl=60)
    def load_csv (): 
        df = pd.read_csv("data/BD_MED.csv", delimiter=";")
        df["Fecha inicial"] = pd.to_datetime(df["Fecha inicial"], infer_datetime_format=True)
        return df
    
    df = load_csv()
    
    # ---- App ----
    with st.container():
        st.write("---")
        left_column,right_column = st.columns(2)
        with left_column:
            st.header("")
            st.write("##")
            
            
    # ---- Project ---- 
    year = st.sidebar.multiselect(
        "Seleccione el Año:",
        options = df["Año"].unique(),
        default=2022
    )
    
    month = st.sidebar.multiselect(
        "Seleccione el Mes:",
        options = df["Mes"].unique(),
        default=['ENERO','FEBRERO']

    )
    
    contractor = st.sidebar.multiselect(
        "Seleccione el Contratista:",
        options=df["Contratista"].unique(),
        default=df["Contratista"].unique(),
    )
    
    
    df_selection = df.query(
        "Año == @year & Mes == @month & Contratista == @contractor"
    )
    
    # ----- Downdload Data -----
    def to_excel(df_selection):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        df_selection.to_excel(writer,index=False, sheet_name="BD_MA")
        workbook= writer.book
        worksheet = writer.sheets["BD_MA"]
        format1 = workbook.add_format({"num_format" : "0"})
        worksheet.set_column("A:A", None, format1)
        writer.save()
        processed_data = output.getvalue()
        return processed_data

    today = date.today()
    today = today.strftime("%d/%m/%Y")
    
    df_selection_xlsx = to_excel(df_selection)
    st.download_button(label="📥 Descargar Excel", data=df_selection_xlsx, file_name="BD_MA_" + today + ".xlsx") 
    
    # ---- Data ----
    
    
    total_inspections = df_selection.groupby(["Código de evaluación"]).size().count()
    most_recent_date = df["Fecha inicial"].max().strftime("%d-%m-%Y")
    percentage  = df_selection["Resultado"].sum() / len(df_selection['Resultado'])
    percentage = int(percentage)
    
    # ----- Top KPI'S ----
    lc, mc, rc = st.columns(3) 
    with lc:
        st.subheader("Datos actualizados al:")
        st.subheader(f"{most_recent_date}")
        
    with mc:
        st.subheader("Total Inspecciones") 
        st.subheader(f"{total_inspections}")    
        
    with rc:
        st.subheader("Cumplimiento Total %") 
        st.subheader(f"{percentage}%")
      
        
         
    # ---- Data ----
    total_inspection_constructor = df_selection.groupby(["Contratista"]).count() / 51
    total_inspection_constructor1 = df_selection.groupby(["Contratista"]).size().sort_values(ascending=False)/ int(51)
    
    fig_inspection_constructor = px.pie(
        total_inspection_constructor,
        names= total_inspection_constructor.index,
        values="Situación",
        color=total_inspection_constructor.index,
        labels= {'color': 'Contratista', 'Situación': 'Cantidad de Inspecciones'},
        title = "Cantidad de Inspecciones por Contratista "
        
        
    )
    fig_inspection_constructor.update_layout(
        annotations=[dict(text='Contratista', x=1.22, y=1.1, font_size=18, showarrow=False)]

    )
    st.plotly_chart(fig_inspection_constructor)
    
        
    button_constructor = st.button("Mostrar Tabla" , key=0)

    if button_constructor == True:
        st.subheader("Cantidad")
        st.table(total_inspection_constructor1)
        button_constructor = st.button("Ocultar Tabla", key=0)
        
    else:
        st.write("")
    
    
    # ---- Data -----
    
    total_supervisor = df_selection.groupby(["Supervisor"]).count().sort_values(by="Contratista",ascending=False) / int(51)
    total_supervisor1 = df_selection.groupby(["Supervisor", "Contratista"]).size().sort_values(ascending=False) / int(51)
    
    # ---- Charts -----
    
    fig_supervisor = px.pie(
    total_supervisor,
    names= total_supervisor.index,
    values="Situación",
    color=total_supervisor.index,
    labels= {'color': 'Supervisor', 'Situación': 'Cantidad de Inspecciones'},
    title = "Cantidad de Inspecciones por Supervisor "
    
    )
    st.plotly_chart(fig_supervisor)
    
    
    button_supervisor = st.button("Mostrar Tabla" , key=1)

    if button_supervisor == True:
        st.subheader("Cantidad")
        st.table(total_supervisor1)
        button_supervisor = st.button("Ocultar Tabla", key=0)
        
    else:
        st.write("")
    
    
    
    st.markdown("---")
    st.subheader("Hallazgos Comunes")
    st.subheader("""
                 Segun los datos no se encuentran hallazgos inferior al 100%""")
    
    st.markdown("----")
    
    # def to_excel(total_finding_data):
    #     output = BytesIO()
    #     writer = pd.ExcelWriter(output, engine="xlsxwriter")
    #     total_finding_data.to_excel(writer, index=False,sheet_name="BD_HALLAZGOS_MA")
    #     worksheet = writer.sheets["BD_HALLAZGOS_MA"]
    #     workbook = writer.book
    #     format1= workbook.add_format({"num_format" : "0"})
    #     worksheet.set_column("A:A",None, format1)
    #     writer.save()
    #     processed_data = output.getvalue()
    #     return processed_data
    
    # total_finding_data_xlsx = to_excel(total_finding_data)
    
    st.markdown("""
    # Descargar BD relacionados a Hallazgos
    Base de datos ya filtrada por hallazgo, se podra visualizar el detalle presionando el boton a continuación.
    """)    
    
    st.download_button(label="📥 Descargar Excel", data="Nonee",file_name="BD_HALLAZGOS_SEGURIDAD" + today + ".xlsx", disabled=True)
    
 
    
    
    