from csv import writer
from datetime import date
from matplotlib.pyplot import text, title
import streamlit as st
import pandas as pd
import numpy as np
from re import sub
from PIL import Image
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import plotly_express as px


def i_obras():
 # ---- Start ---- 
    st.markdown("""
    
    # Dashboard Calidad Técnica Obras Zonal Florida
    
    """
    )
    # ---- Function ----

    @st.cache_data(ttl=60)
    def load_csv ():
        df = pd.read_csv("data/BD_OBRAS.csv", delimiter=";")
        df["FECHA_INSPECCION"] = pd.to_datetime(df["FECHA_INSPECCION"], infer_datetime_format=True)
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
        options=df["AÑO"].unique(),
        default=[2022,2023]
    ) 
    
    
    month = st.sidebar.multiselect(
        "Seleccione el Mes:",
        options=df["MES"].unique(),
        default=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO', 'JULIO', 'AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE'],
    )

    type = st.sidebar.multiselect(
        "Seleccione el Tipo de Obra:",
        options=df["TIPO_OBRA"].unique(),
        default=df["TIPO_OBRA"].unique(),
    )

    contractor = st.sidebar.multiselect(
        "Seleccione el Contratista:",
        options=df["CONTRATISTA"].unique(),
        default=df["CONTRATISTA"].unique(),
    )

    df_selection = df.query(
        "AÑO == @year & MES == @month & TIPO_OBRA == @type & CONTRATISTA == @contractor" 
    )

    # ----- To Excel -----

    def to_excel(df_selection):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        df_selection.to_excel(writer,index=False, sheet_name="BD_OBRAS")
        workbook= writer.book
        worksheet = writer.sheets["BD_OBRAS"]
        format1 = workbook.add_format({"num_format" : "0"})
        worksheet.set_column("A:A", None, format1)
        writer.save()
        processed_data = output.getvalue()
        return processed_data

    today = date.today()
    today = today.strftime("%d/%m/%Y")

    df_selection_xlsx = to_excel(df_selection)
    st.download_button(label="📥 Descargar Excel", data=df_selection_xlsx, file_name="BD_Calidad_Obras_" + today + ".xlsx")   


    # ---- MarkDown ---- 

    # ---- Data ---- 

    total_inspections = df_selection["OT"].count()
    most_recent_date = df["FECHA_INSPECCION"].max().strftime("%d-%m-%Y")
    total_finding = df_selection["HAY HALLAZGO"].str.contains("SI").value_counts()[True]
    
    # --- Data Total Finding "YES" ---- 
    total_finding_constructor = df_selection.loc[df_selection["HAY HALLAZGO"] == "SI"]
    total_finding_constructor1 = total_finding_constructor.groupby(["CONTRATISTA","HAY HALLAZGO"]).size().sort_values(ascending=False)
    total_finding_constructor = total_finding_constructor.groupby(["CONTRATISTA"]).count().sort_values(by="HAY HALLAZGO" ,ascending=True)
    common_finding = df_selection.groupby(["NOMBRE DE INCIDENCIA"]).size()



    # ---- Top KPI'S -----
    lc, mc, rc = st.columns(3)
    with lc:
        st.subheader("Datos actualizados al:")
        st.subheader(f"{most_recent_date}")

    with mc:
        st.subheader("Total Inspecciones")  
        st.subheader(f"{total_inspections}")  
    with rc:
        st.subheader("Total Hallazgos")
        st.subheader(f"{total_finding}")    

    st.markdown("----")

    # ---- Charts ----- 

    fig_constructor_finding = px.bar(
        total_finding_constructor,
        x=total_finding_constructor.index.get_level_values(0),
        y="HAY HALLAZGO",
        color=total_finding_constructor.index.get_level_values(0),
        title="Hallazgos por Contratista",
    )   

    fig_constructor_finding.update_layout(
        plot_bgcolor="rgba (0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
    
    st.plotly_chart(fig_constructor_finding)
    

    button_table_total_finding = st.button("Mostrar Tabla" , key=0)

    if button_table_total_finding == True:
        st.subheader("Cuenta Hallazgo SI/NO")
        st.table(total_finding_constructor1)
        button_table_total_finding = st.button("Ocultar Tabla", key=1)
        
    else:
        st.write("")
    


    
    
    common_finding = df_selection.groupby(["NOMBRE DE INCIDENCIA"]).count().sort_values(by="OT", ascending=True)
    common_finding_detail = df_selection.groupby(["NOMBRE DE INCIDENCIA"]).size().sort_values(ascending=False)
    common_finding_top10 = common_finding.nlargest(10, "OT")


    fig_common_finding = px.pie(
        common_finding_top10,
        names=common_finding_top10.index,
        values="OT",
        color=common_finding_top10.index.get_level_values(0),
        title="Hallazgo Común (Top 10)",
    )
    fig_common_finding.update_layout(
        plot_bgcolor="rgba (0,0,0,0)",
        xaxis=(dict(showgrid=False)),
        annotations=[dict(text='Nombre Hallazgo', x=1.72, y=1.1, font_size=18, showarrow=False)]

    )
    
    
    st.plotly_chart(fig_common_finding)

    button_table_common = st.button("Mostrar Tabla" , key=2)

    if button_table_common == True:
        st.subheader("Hallazgo mas Común")
        st.table(common_finding_detail)
        button_table_common = st.button("Ocultar Tabla", key=3)

    else:
        st.write("")    

    # ---- Data Finding By Constructor ---- 

    finding_by_constructor = df_selection.loc[df_selection["HAY HALLAZGO"] == "SI"]
    finding_by_constructor1 = finding_by_constructor.groupby(["CONTRATISTA","NOMBRE DE INCIDENCIA"]).size().sort_values(ascending=False)
    finding_by_constructor = finding_by_constructor.groupby(["CONTRATISTA","NOMBRE DE INCIDENCIA"]).count().sort_values(by="OT",ascending=True)


    fig_finding_by_constructor = px.bar(
        finding_by_constructor,
        x=finding_by_constructor.index.get_level_values(1),
        y = "HAY HALLAZGO",
        color = finding_by_constructor.index.get_level_values(0),
        text_auto=True,
        title="Cantidad de Hallazgos por tipo y Contratista",
        labels={'x': 'Nombre de Incidencia', 'color':'Contratista'},
        
    )
    fig_finding_by_constructor.update_layout(
        plot_bgcolor="rgba (0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )

    st.plotly_chart(fig_finding_by_constructor)

    button_table_fbc = st.button("Mostrar Tabla" , key=4)

    if button_table_fbc == True:
        st.subheader("Hallazgos por Contratista")
        st.table(finding_by_constructor1)
        button_table_fbc = st.button("Ocultar Tabla", key=5)

    else:
        st.write("")    


    #  ---- Supervisor Finding ----

    # ---- Data for Finding by Supervisor ----- 


    supervisor_total_finding = df_selection.loc[df_selection["HAY HALLAZGO"] == "SI"]
    supervisor_total = supervisor_total_finding.groupby(["SUPERVISOR","CONTRATISTA"]).size().sort_values(ascending=False)
    supervisor_total_finding = supervisor_total_finding.groupby(["SUPERVISOR"]).count().sort_values(by="OT", ascending=True)
    

    fig_supervisor_total_finding = px.bar(
        supervisor_total_finding,
        x=supervisor_total_finding.index,
        y="HAY HALLAZGO",
        color=supervisor_total_finding.index.get_level_values(0),
        text_auto=True,
        title="Cuenta Hallazgos por Supervisor"

    )

    fig_supervisor_total_finding.update_layout(
        plot_bgcolor="rgba (0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
    st.plotly_chart(fig_supervisor_total_finding)

    button_supervisor_total = st.button("Mostrar Tabla", key=6)

    if button_supervisor_total == True:
        st.subheader("Hallazgos por Supervisor")
        st.table(supervisor_total)
        button_supervisor_total = st.button("Ocultar Tabla", key=7)

    else:
        st.write("")   


    st.markdown("---")

    # ---- Data by NV ---- 

    total_by_nv = df_selection.loc[df_selection["HAY HALLAZGO"] == "SI"]
    total_by_nv = total_by_nv.groupby(["OT","CONTRATISTA","ITO","TIPO_OBRA"]).size().sort_values(ascending=False)
    total_by_si = df_selection.loc[df_selection["HAY HALLAZGO"] == "SI"]
    total_by_si = total_by_si.loc[:,["OT","NV/GOM","DIRECCION","ITO","FECHA_INSPECCION","SUPERVISOR","TIPO_TRABAJO","HAY HALLAZGO", "NOMBRE DE INCIDENCIA","MES","AÑO","TIPO_OBRA"]]

    # ---- Excel Data Loc by "SI"----

    def to_excel_si(total_by_si):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        total_by_si.to_excel(writer, index=False,sheet_name="BD_CALIDAD_HALLAZGOS")
        worksheet = writer.sheets["BD_CALIDAD_HALLAZGOS"]
        workbook = writer.book
        format1= workbook.add_format({"num_format" : "0"})
        worksheet.set_column("A:A",None, format1)
        writer.save()
        processed_data = output.getvalue()
        return processed_data

    
    df_selection_finding_xlsx = to_excel_si(total_by_si)
    st.markdown("""
    # Descargar BD relacionados a Hallazgos
    Base de datos ya filtrada por hallazgo, se podra visualizar el detalle presionando el boton a continuación.
    """)

    st.download_button(label="📥 Descargar Excel", data=df_selection_finding_xlsx, file_name="BD_CALIDAD_HALLAZGOS_" + today + ".xlsx")     


  

 
