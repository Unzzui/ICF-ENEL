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


def i_seg():
    
    st.markdown("""
                
    # Dashboard Seguridad Zonal Florida
    
    """)
    
    @st.cache_data(ttl=60)
    def load_csv_security():
        df = pd.read_csv("data/BD_SEG_FLORIDA.csv", delimiter=";")
        df["Avisos"] = pd.to_datetime(df["Avisos"],infer_datetime_format=True)
        return df

    df = load_csv_security()

    with st.container():
        lcs, rcs = st.columns(2)
        with lcs:
            st.header("")
            st.write("##")

    today = date.today()
    today = today.strftime("%d/%m/%Y")
    # ---- Security Proyect 

    st.sidebar.header("Filtre Aqui:")
    
    
    year = st.sidebar.multiselect(
        "Seleccion el Año:",
        options = df["Año"].unique(),
        default = df["Año"].unique(),
    )
    month = st.sidebar.multiselect(
        "Seleccione el Mes:",
        options = df["Mes"].unique(),
        default = df["Mes"].unique(),
    )

    contractor = st.sidebar.multiselect(
        "Seleccione el Contratista:",
        options=df["Contratista"].unique(),
        default=df["Contratista"].unique(),
    )



        
    df_selection = df.query(
        "Año == @year & Mes == @month & Contratista == @contractor"
    )
    
    def to_excel(df_selection):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        df_selection.to_excel(writer,index=False, sheet_name="BD_SEGURIDAD")
        workbook= writer.book
        worksheet = writer.sheets["BD_SEGURIDAD"]
        format1 = workbook.add_format({"num_format" : "0"})
        worksheet.set_column("A:A", None, format1)
        writer.save()
        processed_data = output.getvalue()
        return processed_data

    today = date.today()
    today = today.strftime("%d/%m/%Y")

    df_selection_xlsx = to_excel(df_selection)
    st.download_button(label="📥 Descargar Excel", data=df_selection_xlsx, file_name="BD_SEGURIDAD_" + today + ".xlsx")   
    
    # ---- Data ---- 
    most_recent_date =  df["Avisos"].max().strftime("%d-%m-%Y")
    total_inspections = int(len(df_selection["N° Inspeccion"]))
    total_finding_data = df_selection.loc[df_selection["SEVERIDAD"] != "Sin hallazgo" ]
    total_finding_sum = total_finding_data.groupby(["SEVERIDAD"]).size().sum() 
    total_finding = total_finding_data.sort_values(by="SEVERIDAD",ascending=False)
    severity = total_finding_data.groupby(["SEVERIDAD"]).size().sort_values(ascending=False)
    # ---- Top KPI's ----
    
    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        st.subheader("Datos actualizados al: ")
        st.subheader(f"{most_recent_date}")
    with middle_column:
        st.subheader("Total Inspecciones:")
        st.subheader(f"{total_inspections}")   
    with right_column:
        st.subheader("Total Hallazgos")
        st.subheader(f"{total_finding_sum}")     

    # ---- Finding Evolution ---- 
    
    orden_date = ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO', 'JULIO', 'AGOSTO',
    'SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']

    total_finding_data["Mes"] = pd.Categorical(total_finding_data["Mes"], orden_date)
    finding_evolution = total_finding_data.groupby(["Mes","Año"]).count()
    finding_evolution1 = total_finding_data.groupby(["Mes", "Año"]).size().sort_values(ascending=False)
    
    
    fig_evolution_finding = px.line(
        finding_evolution,
        x= finding_evolution.index.get_level_values("Mes"),
        y= "Incumplimiento",
        color = finding_evolution.index.get_level_values("Año"),
        labels={'x': 'Mes', 'color':'Año'},
        title="Evolutivo"
    )
    
    
    st.plotly_chart(fig_evolution_finding)
    
    button_evolution_finding = st.button("Mostrar Tabla" , key=0)

    if button_evolution_finding == True:
        st.subheader("Evolutivo")
        st.table(finding_evolution1)
        button_evolution_finding = st.button("Ocultar Tabla", key=1)
        
    else:
        st.write("")

    st.markdown("----")
    
    
    # ---- Pie Chart Finding Security ---- 
    
    fig_total_finding = px.pie(
        total_finding,
        names="SEVERIDAD",
        values="SEVERIDAD",
        color="SEVERIDAD",
    )
    fig_total_finding.update_layout(
        
    title_text="Hallazgo según Severidad",
    plot_bgcolor="rgba (0,0,0,0)",
    annotations=[dict(text='Severidad', x=1.05, y=1.1, font_size=20, showarrow=False)]
    ) 
    st.plotly_chart(fig_total_finding)
    
    
    
    button_table_total_finding = st.button("Mostrar Tabla" , key=2)

    if button_table_total_finding == True:
        st.subheader("Detalle por Severidad")
        st.table(severity)
        button_table_total_finding = st.button("Ocultar Tabla", key=3)
        
    else:
        st.write("")

    st.markdown("----")


    # ----- Contractor Data ----- 

    total_contractor_finding = total_finding_data.groupby(["Contratista"]).count().sort_values(by="Incumplimiento", ascending=True)
    total_contractor_finding1 = total_finding_data.groupby(["Contratista"]).size().sort_values(ascending=False)

    fig_finding_by_constructor = px.bar(
    total_contractor_finding,
    x=total_contractor_finding.index,
    y = "Incumplimiento",
    color = total_contractor_finding.index,
    text_auto=True,
    title="Hallazgos por Contratista"
    )

    fig_finding_by_constructor.update_layout(
        plot_bgcolor="rgba (0,0,0,0)",
        xaxis=(dict(showgrid=False)),
    )
    st.plotly_chart(fig_finding_by_constructor)

    button_table_total_contructor = st.button("Mostrar Tabla" , key=4)

    if button_table_total_contructor == True:
        st.subheader("Detalle por Severidad")
        st.table(total_contractor_finding1)
        button_table_total_contructor = st.button("Ocultar Tabla", key=5)
        
    else:
        st.write("")

    

    # ---- Data Common Finding ---- 
    common_finding = total_finding_data.groupby(["Incumplimiento", "Nombre del Incumplimiento"]).count().sort_values(by="N° Inspeccion",ascending=False)
    common_finding1 = total_finding_data.groupby(["Incumplimiento","SEVERIDAD", "Nombre del Incumplimiento"]).size().sort_values(ascending=False)

    fig_common_finding = px.pie(
        common_finding,
        names= common_finding.index.get_level_values(0),
        values="N° Inspeccion",
        color=common_finding.index.get_level_values(1),
        title= "Hallazgos Comunes",
    )
    fig_common_finding.update_layout(
        annotations=[dict(text='Codigo Hallazgo', x=1.12, y=1.1, font_size=20, showarrow=False)]

    )

    st.plotly_chart(fig_common_finding)
    
    button_table_common_finding = st.button("Mostrar Tabla" , key=6)

    if button_table_common_finding == True:
        st.subheader("Hallazgos Comunes")
        st.table(common_finding1)
        button_table_common_finding = st.button("Ocultar Tabla", key=7)
        
    else:
        st.write("")

    
    
    st.markdown("---")
    
    # ---- Most Finding By Supervisor ----
    
    finding_supervisor = total_finding_data.groupby(["Supervisor"]).count().sort_values(by="N° Inspeccion", ascending=True)
    finding_supervisor1 = total_finding_data.groupby(["Supervisor","Contratista"]).size().sort_values(ascending=False)
    
    fig_finding_supervisor = px.bar(
    finding_supervisor,
        x = finding_supervisor.index,
        y = "Incumplimiento",
        color = finding_supervisor.index,
        title = "Hallazgos por Supervisor"
        )
    fig_finding_supervisor.update_layout(
        plot_bgcolor="rgba (0,0,0,0)",
        xaxis=(dict(showgrid=False)),
    )
    st.plotly_chart(fig_finding_supervisor)
    
    
    button_table_supervisor_finding = st.button("Mostrar Tabla" , key=8)

    if button_table_supervisor_finding == True:
        st.subheader("Cantidad de Hallazgos por Supervisor")
        st.table(finding_supervisor1)
        button_table_supervisor_finding = st.button("Ocultar Tabla", key=9)
        
    else:
        st.write("")
    
    
    st.markdown("---")
    
    def to_excel(total_finding_data):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        total_finding_data.to_excel(writer, index=False,sheet_name="BD_HALLAZGOS_SEGURIDAD")
        worksheet = writer.sheets["BD_HALLAZGOS_SEGURIDAD"]
        workbook = writer.book
        format1= workbook.add_format({"num_format" : "0"})
        worksheet.set_column("A:A",None, format1)
        writer.save()
        processed_data = output.getvalue()
        return processed_data
    
    total_finding_data_xlsx = to_excel(total_finding_data)
    
    st.markdown("""
    # Descargar BD relacionados a Hallazgos
    Base de datos ya filtrada por hallazgo, se podra visualizar el detalle presionando el boton a continuación.
    """)    
    
    st.download_button(label="📥 Descargar Excel", data=total_finding_data_xlsx, file_name="BD_HALLAZGOS_SEGURIDAD_" + today + ".xlsx")     

