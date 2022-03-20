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

def i_inmb():

    st.markdown("""

    #  DashBoard Calidad Técnica Inmobiliario 
    
    """)

    @st.cache(ttl=60)
    def load_csv():
        df = pd.read_csv("data/BD_INMOBILIARIO.csv", delimiter=";")
        df["FECHA INSPECCIÓN"] = pd.to_datetime(df["FECHA INSPECCIÓN"], infer_datetime_format=True)
        df = df.rename (columns ={"CLIENTE CONFORME" :"CONFORMIDAD DEL CLIENTE"})
        return df

    df = load_csv()

    with st.container():
        st.write("---")
        left_column,right_column = st.columns(2)
        with left_column:
            st.header("")
            st.write("##")
 

# ---- Project -----

    st.sidebar.header("Filtre Aqui:")

    year = st.sidebar.multiselect(
        "Seleccione el Año:",
        options=df["AÑO"].unique(),
        default=2022
    )

    month = st.sidebar.multiselect(
        "Seleccione el Mes:",
        options= df["MES"].unique(),
        default=df["MES"].unique(),
    )



    df_selection = df.query (
        "AÑO == @year & MES ==@month "
    )


# ---- To Excel -----

    def to_excel(df_selection):
        output= BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        df_selection.to_excel(writer, index=False, sheet_name="BD_IMN")
        workbook = writer.book
        worksheet = writer.sheets["BD_IMN"]
        format1 = workbook.add_format({"num_format": "0.00"})
        worksheet.set_column("A:A", None, format1)
        writer.save()
        processed_data = output.getvalue()
        return processed_data

    today = date.today()
    today = today.strftime("%d/%m/%Y")

    df_selection_xlsx = to_excel(df_selection)
    st.download_button(label="📥 Descargar Excel",data=df_selection_xlsx,file_name="BD_Calidad_Inmobiliario" + today + ".xlsx")  


# ---- MarkDown ----


# ---- Data ----

    most_recent_date = df["FECHA INSPECCIÓN"].max().strftime("%d-%m-%Y")
    total_inspections = int(len(df["NV"]))
    total_selected_inspections = int(len(df_selection["NV"]))
    total_finding = df_selection["OBSERVACIONES DE MULTA"].value_counts().sum()

    total_finding_chart = df_selection["OBSERVACIONES DE MULTA"].value_counts()



# ---- Top KPI'S ----
    lc, mc, rc = st.columns(3)
    with lc:
        st.subheader("Datos actualizados al: ")
        st.subheader(f"{most_recent_date}")
    with mc:
        st.subheader("Total Inspecciones")
        st.subheader(f"{total_selected_inspections}")    

    with rc:
        st.subheader("Total Hallazgos")
        st.subheader(f"{total_finding}")

    

    st.markdown("----")

    fig_finding = px.bar (
        total_finding_chart,
        x=total_finding_chart.index,
        y="OBSERVACIONES DE MULTA",
        orientation="v",
        color=total_finding_chart.index.get_level_values(0),
        title="<b>Hallazgos</b>",
        template="plotly_white",
    )


    fig_finding.update_layout(

        plot_bgcolor="rgba (0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )

    st.plotly_chart(fig_finding)
    st.table(total_finding_chart)



    quality_data = df_selection["ESTADO DEL TRABAJO EN TERRENO"].value_counts()


    fig_quality = px.pie (
        quality_data,
        values="ESTADO DEL TRABAJO EN TERRENO",
        names = quality_data.index,
        title="<b>Calidad Ejecución</b>"
    )

    st.plotly_chart(fig_quality)
    st.table(quality_data)

    orden_date = ['ENERO','FEBRERO']

    # ,'MARZO','ABRIL','MAYO','JUNIO', 'JULIO', 'AGOSTO',
    # 'SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']

    df_selection["MES"] = pd.Categorical(df_selection["MES"], orden_date)

    quality_chart = df_selection.groupby(["MES","MULTA SI/NO"]).count()

    quality_chart1 = df_selection.groupby(["MES","MULTA SI/NO"]).size()


    fig_evolution_penalty = px.line (
        quality_chart,
        x=quality_chart.index.get_level_values(0),
        y="OBS INSPECTOR",
        title="<b>Evolución Multas Si/No</b>",
        color=quality_chart.index.get_level_values(1), 
        markers=True
    )

    st.plotly_chart(fig_evolution_penalty)
    st.table(quality_chart1)


    # ----- Clients Info -----

    st.markdown("---")
    st.markdown("""

    # Detalle Conformidad Cliente
    """)

    # ---- Data ----

    total_clients = df_selection["CONFORMIDAD DEL CLIENTE"].count()

    total_aprove_clients = df_selection["CONFORMIDAD DEL CLIENTE"].str.contains("Cliente conforme").value_counts()[True]

    total_rejected_clients = df_selection["CONFORMIDAD DEL CLIENTE"].str.contains("Cliente disconforme").value_counts()[True]

    data_clients = df_selection["CONFORMIDAD DEL CLIENTE"].value_counts().sort_values(ascending=False)

    # ---- KPI'S -----

    right_column_clients, middle_column_clients,left_column_clients = st.columns(3)

    with right_column_clients:
        st.subheader("Total Inspecciones")
        st.subheader(f"{total_clients}")

    with middle_column_clients:
        st.subheader("Clientes Conformes")
        st.subheader(f"{total_aprove_clients}")

    with left_column_clients:
        st.subheader("Clientes Disconfomes")
        st.subheader(f"{total_rejected_clients}")    


    st.markdown("----")    

    # ---- Clients Chart ---- 


    fig_clients = px.pie(
        data_clients,
        names=data_clients.index,
        values="CONFORMIDAD DEL CLIENTE",
        title="<b>Conformidad Cliente</b>",
    )

    fig_clients.update_layout(

        plot_bgcolor="rgba (0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )

    st.plotly_chart(fig_clients)
    st.table(data_clients)
    st.write(total_aprove_clients)
    
