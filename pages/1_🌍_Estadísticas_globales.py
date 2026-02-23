
import streamlit as st
import pandas as pd
import numpy as np

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import *

sentimientos, odio = cargar_datos_de_la_cache()

# ----------------------------------

top_emojis = obtener_emojis_mas_comunes(sentimientos)

st.title("🌍 Estadísticas globales")


c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric(label="Mensajes totales", value=sentimientos.shape[0])

messages_with_marina = sentimientos.loc[sentimientos['message'].str.contains("Marina", case=False, na=False, regex=False), ['date', 'timestamp', 'author', 'message']]
    
coincidencias_with_marina = str(messages_with_marina.shape[0])
with c2: 
    st.metric(label="Veces dicho Marina", value=coincidencias_with_marina)

messages_with_humo = sentimientos.loc[sentimientos['message'].str.contains("humo", case=False, na=False, regex=False), ['date', 'timestamp', 'author', 'message']]
    
coincidencias_with_humo = str(messages_with_humo.shape[0])

with c3: 
    st.metric(label="Veces dicho humo", value=coincidencias_with_humo)

    messages_with_rent = sentimientos.loc[sentimientos['message'].str.contains("rent", case=False, na=False, regex=False), ['date', 'timestamp', 'author', 'message']]
    
    coincidencias_with_rent = str(messages_with_rent.shape[0])

with c4: 
    st.metric(label="Veces dicho renta", value=coincidencias_with_rent)

tab_general, tab_emotions, tab_sentiments, tab_hate = st.tabs(['💬 General', '😊 Emociones', '👍 Sentimientos', '🤬 Odio'])

with tab_general:
    df_mensajes = (
        sentimientos.groupby('author')
        .count()['message']
        .sort_values(ascending=False)
        .reset_index()
    )
    
    #df_mensajes['emojis'] = emojis_campeon
    
    leaderboard_mensajes = (alt.Chart(df_mensajes)
        .mark_bar(cornerRadiusBottomRight=5,cornerRadiusTopRight=5)
        .encode(
            x=alt.X("message:Q", title="💬"),
            y=alt.Y("author:N", sort='-x', title="👥"),
            color=alt.Color(
                "author", 
                scale=alt.Scale(domain=list(usuarios_colormap.keys()), range=usuarios_colormap.values()), 
                legend=None
            ),
            tooltip=[
                alt.Tooltip("message:Q", title="Cantidad")
            ]
        )
    )
    
    
    
    sentimientos['es_risa'] = sentimientos['message'].str.contains('jaj|😂|🤣', case=False, na=False, regex=True)
    
    df_risa = (
        sentimientos[sentimientos['es_risa']].groupby('author')['message']
        .count()
        .sort_values(ascending=False)
        .head(3)
        .reset_index()
    
    )
    df_risa['emojis'] = emojis_campeon
    
    df_risa_porcentual = (
        sentimientos.groupby('author')['es_risa']
        .mean()
        .mul(100)
        .sort_values(ascending=False)
        .head(3)
        .reset_index()
    )
    df_risa_porcentual['emojis'] = emojis_campeon
    
    leaderboard_risa = bar_chart(
        source=df_risa,
        category='author',
        value='message',
        label_col='emojis',
        var_title='Usuarios',
        color_map=usuarios_colormap
    )
    
    leaderboard_risa_porcentual = bar_chart(
        source=df_risa_porcentual,
        category='author',
        value='es_risa',
        label_col='emojis',
        var_title='Usuarios',
        color_map=usuarios_colormap
    )
    
    st.header("Clasificación")
    
    
    c1, c2 = st.columns([0.35, 0.7])
    with c1:
        # Creamos las posiciones para el dataframe de posicion
        medallas = []
        for i in range(len(df_mensajes)):
            if i == 0:
                medallas.append(":yellow-badge[:material/crown: 1º]")
            elif i == 1:
                medallas.append(":gray-badge[2º]")
            elif i == 2:
                medallas.append(":orange-badge[3º]")
            else:
                medallas.append(f":blue-badge[{i+1}º]")
                
            
        df_mensajes['Pos.'] = medallas
        df_mensajes.set_index('Pos.', inplace=True)
        df_mensajes.rename(columns={'message': '💬'}, inplace=True)

        df_mensajes['👤'] = df_mensajes["author"].apply(
            lambda x: f"[{x}](<Estadísticas_personales?user_search={x}>)"
        )
        
        st.table(df_mensajes[['👤', '💬']], border='horizontal')

    with c2:
        # Tabla Github --
        sentimientos['count'] = 1
    
        github_table = alt.Chart(sentimientos).mark_circle().encode(
            x=alt.X('hours(timestamp):O', title=""),
            y=alt.Y('day(timestamp):O', title=""),
            size=alt.Size('sum(count):Q', title="Nº de mensajes",
                legend=alt.Legend(
                    orient='top',     
                    direction='horizontal', 
                    #gradientLength=200 
                )
            ),
            color=alt.Color('sum(count):Q', 
                scale=alt.Scale(scheme='reds'),
                
            )
        )

        # --- Gráfico de Barras inferior ---
        hours_bar_chart = alt.Chart(sentimientos).mark_bar(color='firebrick').encode(
            x=alt.X('hours(timestamp):O', title="Horas"),
            y=alt.Y('sum(count):Q', title=""),
            tooltip=[
                alt.Tooltip('hours(timestamp):O', title='Hora'),
                alt.Tooltip('sum(count):Q', title='Total')
            ],
            #color=alt.Color('sum(count):Q', 
            #    scale=alt.Scale(scheme='reds'),  
            #)
        ).properties(height=150)
        
        grafico_final = alt.vconcat(
            github_table,
            hours_bar_chart).resolve_scale(
            x='shared' 
        )
            
        st.altair_chart(grafico_final, use_container_width=True)
        
        st.header("Emoticonos")
        emoji_chart = bar_chart(top_emojis, category='Emoji', value = 'Cantidad', var_title="Emojis")
        st.altair_chart(emoji_chart)
        
with tab_emotions:
    st.header("En construcción")
    st.image("https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdGs4ZDh0ZzJzMXQ4N2Z3bm5za3Vhd24yZTdpZWk1bG52MTBrcWEyaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/H6cmWzp6LGFvqjidB7/giphy.gif")

with tab_sentiments:
    st.header("En construcción")
    st.image("https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdGs4ZDh0ZzJzMXQ4N2Z3bm5za3Vhd24yZTdpZWk1bG52MTBrcWEyaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/H6cmWzp6LGFvqjidB7/giphy.gif")
    
with tab_hate:
    st.header("En construcción")
    st.image("https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdGs4ZDh0ZzJzMXQ4N2Z3bm5za3Vhd24yZTdpZWk1bG52MTBrcWEyaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/H6cmWzp6LGFvqjidB7/giphy.gif")
    


