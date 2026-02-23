import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from streamlit_theme import st_theme

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import *
from whatsapp_engine import generar_html_whatsapp

sentimientos, odio = cargar_datos_de_la_cache()

# --------------------------

st.title("🔎 Buscador de palabras")

word = st.text_input("Introduce una palabra para buscarla en el chat", value=None)

if word:
    messages_with_word = sentimientos.loc[sentimientos['message'].str.contains(word, case=False, na=False, regex=False), ['date', 'timestamp', 'author', 'message']]
    
    coincidencias = str(messages_with_word.shape[0])
    
    st.metric(label="Coincidencias", value=coincidencias)
    
    bar_chart_usuarios = bar_chart(
        source = messages_with_word.groupby('author').count()['message'].reset_index(),
        category = 'author',
        value = 'message',
        var_title = 'Usuarios'
    )
    
    st.altair_chart(bar_chart_usuarios) 
    
    # Para que se vean todos los dias debemos añadirlos de forma artificial (Optimiz)
    # 1. Agrupamos y contamos los mensajes de tu dataframe filtrado
    conteo_diario = messages_with_word.groupby('date').count()['message']
    
    # 2. Aseguramos que el índice sea de tipo fecha
    conteo_diario.index = pd.to_datetime(conteo_diario.index)
    
    # 3. Creamos un rango con TODAS las fechas de tu DataFrame original 'sentimientos'
    fecha_inicio = pd.to_datetime(sentimientos['date']).min()
    fecha_fin = pd.to_datetime(sentimientos['date']).max()
    rango_fechas = pd.date_range(start=fecha_inicio, end=fecha_fin)
    
    # 4. Reindexamos obligando a que estén todas las fechas. Las que no existan, se rellenan con 0
    conteo_diario = conteo_diario.reindex(rango_fechas, fill_value=0)
    
    # 5. Convertimos a DataFrame para Streamlit, renombrando la columna de fechas
    datos_grafico = conteo_diario.reset_index()
    
    # 6. Dibujamos el gráfico
    chart = alt.Chart(datos_grafico).mark_line(interpolate='monotone').encode(
        x=alt.X('index:T', title="Fecha"),
        y=alt.Y('message:Q', title="Uso")
    )
    st.altair_chart(chart)

    st.columns([0.1, 0.8, 0.1])
    theme = st_theme()
    st.html(
        generar_html_whatsapp(
            messages_with_word[['timestamp', 'date', 'author', 'message']],
            theme,
            max_width="350px"
        )
    )