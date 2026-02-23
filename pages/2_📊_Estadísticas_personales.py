import streamlit as st
import pandas as pd
import numpy as np
from streamlit_theme import st_theme

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import *
from whatsapp_engine import generar_html_whatsapp

sentimientos, odio = cargar_datos_de_la_cache()

# Calculamos las insignias
if "insignias_palabras" not in st.session_state:
  st.session_state["insignias_palabras"] = calcular_insignias_palabras(sentimientos)

if "insignias_comportamiento" not in st.session_state:
    st.session_state["insignias_comportamiento"] = calcular_insignias_comportamiento(sentimientos, odio)


query_dict = st.query_params
user_from_url = query_dict.get("user_search", "")

# --------------------------

st.title("📊 Estadísticas personales")

# Calculamos cuantos usuarios hay en la base de datos
total_users = sentimientos['author'].unique()

user = st.selectbox("Selecciona un usuario para ver sus estadísticas", total_users, placeholder="Elige una opción", index=None)

if user is None and user_from_url != "":
    user = user_from_url

if user:
    st.header(f"{emoji_users[user]} {user}")
    
    # Añadimos las insignias del usuario
    badge_text = ""
    
    for palabra, datos in st.session_state["insignias_palabras"].items():
        # Comprobamos si el usuario actual es el ganador de esa palabra
        if datos["ganador"] == user:
            # Añadimos la insignia al texto (con un espacio al final por si tiene varias)
            badge_text += f":violet-badge[:material/star: Persona que más veces ha dicho '{palabra}' ({datos['veces']})] "
    # Si el texto no está vacío (es decir, ganó al menos una insignia), lo mostramos
    if badge_text:
        st.markdown(badge_text)

    badge_text = ""

    # Recorremos el nuevo diccionario de comportamiento
    for titulo_insignia, datos in st.session_state["insignias_comportamiento"].items():
        if datos["ganador"] == user:
            badge_text += f":yellow-badge[:material/person: {titulo_insignia} ({datos['veces']})] "
    
    if badge_text:
        st.markdown(badge_text)
    
    sentiment_log = buscar_mensajes_usuario(user, sentimientos)
    
    # Estadísticas
    total_mensajes = str(sentiment_log.shape[0])
    porcentaje_risa = sentiment_log['message'].str.contains('jaj|😂|🤣', case=False, na=False, regex=True).mean() * 100
    porcentaje_susp = sentiment_log['message'].str.contains('...', na=False, regex=False).mean() * 100
    porcentaje_comillas = sentiment_log['message'].str.contains(r'".+?"|\'.+?\'', na=False, regex=True).mean() * 100
    
    sentiment_log = sentiment_log[sentiment_log['emotions'] != 'others']
    
    hate_log = buscar_mensajes_usuario(user, odio)
    
    emotions_per_day = desglosar_variable_por_dia(sentiment_log, 'emotions') # Tiene el dia en 'date' y la cantidad de emociones
    sentiments_per_day = desglosar_variable_por_dia(sentiment_log, 'sentiments')
    hate_per_day = desglosar_variable_por_dia(hate_log, 'odio')
    
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Mensajes", value=total_mensajes)
    with c2: 
        st.metric(label="Risa", value=f"{porcentaje_risa:.2f} %")
    with c3: 
        st.metric(label="Puntos suspensivos", value=f"{porcentaje_susp:.2f} %")
    with c4: 
        st.metric(label="Comillas", value=f"{porcentaje_comillas:.2f} %")
    
    
    st.header("Emociones")
    df_emotions_bar_chart = agregar_variables_desglosadas(emotions_per_day, 'emotions')
    emotion_chart = bar_chart(
        df_emotions_bar_chart,
        'emotions',
        'count',
        label_col='emotions_emoji',
        var_title="Emoción",
        color_map=emotion_color_map
    )
    st.altair_chart(emotion_chart)
    
    st.header("Sentimientos")
    df_sentiments_bar_chart = agregar_variables_desglosadas(sentiments_per_day, 'sentiments')
    sentiments_chart = bar_chart(
        df_sentiments_bar_chart,
        'sentiments',
        'count',
        label_col='emotions_emoji', 
        var_title="Sentimiento",
        color_map=emotion_color_map
    )
    st.altair_chart(sentiments_chart)
    
    st.header("Discurso de odio")
    df_hate_bar_chart = agregar_variables_desglosadas(hate_per_day, 'odio')
    hate_chart = bar_chart(
        df_hate_bar_chart,
        'odio',
        'count',
        label_col='emotions_emoji', 
        var_title="Tipo de odio",
        color_map=emotion_color_map
    )
    st.altair_chart(hate_chart)

    #st.dataframe(hate_log)
    st.header("Últimos mensajes")
    
    primer_dia = hate_log.tail(1)['date'].iloc[0]
    ultimo_dia = hate_log.head(1)['date'].iloc[0]
    

    with st.form("my_form", border=False):
        form_col1, form_col2 = st.columns(2)
        with form_col1:
            max_msg = st.number_input(
                "Cantidad de mensajes a mostrar",
                min_value=1,
                max_value=None,
                value=7,
                step=1
            )
        with form_col2:
            dates = st.date_input(
                "Elige fechas para filtrar",
                (primer_dia, ultimo_dia),
                #help="Las fechas deben estar en formato YYYY/MM/DD",
                format="YYYY/MM/DD"
            )
            
            st.form_submit_button(label='Filtrar')

    mask = (hate_log['date'] >= dates[0]) & (hate_log['date'] <= dates[1])
    df_filtrado_fechas = hate_log[mask]
    "---"
    # Para cambiar el tema de los chats
    theme = st_theme()
    c_chat_general, c_chat_odio = st.columns(2)
    with c_chat_general:
        st.subheader("General")
        st.html(generar_html_whatsapp(df_filtrado_fechas.head(max_msg), theme))
    with c_chat_odio:
        st.subheader("Odio")
        st.html(generar_html_whatsapp(df_filtrado_fechas[df_filtrado_fechas['odio'] != ""].drop_duplicates(subset=['timestamp']).head(max_msg), theme))

    