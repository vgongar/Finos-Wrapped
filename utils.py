import emoji
from collections import Counter
import pandas as pd
import streamlit as st
import datetime as dt
import altair as alt
import numpy as np

emojis = {
    'anger': '😡',
    'disgust': '🤢',
    'fear': '😱',
    'joy': '😄',
    'sadness': '☹️',
    'surprise': '😯',
    'POS': '👍',
    'NEG': '👎',
    'NEU': '😐',
    'aggressive': '🤬',
    'hateful': '🖕',
    'targeted': '👊'
}

emotion_color_map = {
    'anger': '#e31f09', # rojo
    'disgust': '#039c2c', # verde
    'fear': '#19559e', # azul
    'joy': '#ffe063', # amarillo
    'sadness': '#6842ff', # morado
    'surprise': '#e359e1', # rosa

    'POS': '#039c2c', # rojo
    'NEG': '#e31f09', # verde
    'NEU': '#ffe063', # ámbar

    'aggressive': '#e31f09', # rojo
    'hateful': '#6842ff', # morado
    'targeted': '#ffe063' # amarillo
}

emojis_campeon = ["🥇","🥈","🥉"]

usuarios_colormap = {
    "Pedro": '#e31f09',
    "Pabloflux": '#039c2c',
    "Álvaro": '#19559e',
    "Gabi": '#ffe063',
    "vic": '#6842ff',
    "Pastor": '#e359e1',
    "Juanba": '#ffe063',
    "Tanke": '#e31f09',
    "Pablo Miluy": '#039c2c',
    "Jose": '#19559e',
    "JJ": '#19559e',
    "Dani": '#e31f09',
    "Gonzalo": '#ffe063',
    "Miguel": '#6842ff',
    "Guti": '#039c2c',
    "Meta AI": '#19559e',
    "Decano": '#19559e',
    "Joe": '#e31f09',
    "Fluxpablo": '#6842ff',
    "Javi": '#e359e1'
}

users_names = {
    "Pedro": 'Pedro',
    "Pabloflux": 'Pabloflux',
    "Alvaro Mates": 'Álvaro',
    "Gabi Mates": 'Gabi',
    "vic": 'vic',
    "David Pastor Sánchez": 'Pastor',
    'juanba el “chetao”': 'Juanba',
    "Antonio Sánchez Mates": 'Tanke',
    'Guárdame a mi como Pablo "Climate Risk Analyst Intern" Mates': 'Pablo Miluy',
    "Jose Mates": 'Jose',
    "Jj Mates": 'JJ',
    "Dani God Mates": 'Dani',
    "Gonzalo Mates": 'Gonzalo',
    "Miguel Roldán": 'Miguel',
    "guti no quiere que le llamen guti": 'Guti',
    "Meta AI": 'Meta AI',
    "Decano Ciencias": 'Decano',
    "Joe Mates": 'Joe',
    "~ Pabloobp": 'Fluxpablo',
    "Javi Bot": 'Javi'
}

emoji_users = {
    "Pedro": "🏳️‍🌈", 
    "Pabloflux": "🤖",
    "Álvaro": "🏃",
    "Gabi": "🍦",
    "vic": "😳",
    "Pastor": "🌎",
    "Juanba": "🕵️‍♂️",
    "Tanke": "🚚",
    "Pablo Miluy": "🗣️",
    "Jose": "👻",
    "JJ": "💊",
    "Dani": "👄",
    "Gonzalo": "👨‍🦲",
    "Miguel": "🧠",
    "Guti": "🍑",
    "Meta AI": "🤖",
    "Decano": "🐟",
    "Joe": "🤠",
    "Fluxpablo": "❓",
    "Javi": "☝️"
}

@st.cache_data
def obtener_emojis_mas_comunes(df, columna='message', top_n=10):
    # 1. Extraemos todos los emojis de todos los mensajes
    todos_los_emojis = []
    
    for texto in df[columna].astype(str):
        # emoji.analyze() encuentra cada emoji en el texto
        encontrados = [res.chars for res in emoji.analyze(texto)]
        todos_los_emojis.extend(encontrados)
    
    # 2. Contamos las frecuencias
    conteo = Counter(todos_los_emojis)
    
    # 3. Lo convertimos a un DataFrame para que sea fácil de mostrar
    df_emojis = pd.DataFrame(conteo.most_common(top_n), columns=['Emoji', 'Cantidad'])
    return df_emojis

def cargar_datos_de_la_cache():
    """
    En caché hay un archivo llamado .
    Ahí viene la fecha de la última actualización. Con esa
    información podemos acceder a los dataframes que ya están
    cargados en la caché
    """
    file_name = "ultima_actualización.txt"
    last_update = st.session_state[file_name]

    df_sentimientos = st.session_state[f"sentimientos_hasta_{last_update}.csv"]
    df_odio = st.session_state[f"odio_hasta_{last_update}.csv"]

    return df_sentimientos, df_odio


def buscar_mensajes_usuario(user, source):
    mask = (source['author'] == str(user))
    return source[mask]
    
def buscar_mensajes_usuarios(users, messages):
    # Extraemos los mensajes de todos los usuarios seleccionados
    users_messages = {}
    for user in users:
        users_messages[str(user)] = buscar_mensajes_usuario(user, messages)
    return users_messages

def desglosar_variable_por_dia(source, var_name):
    """
    Calcula una tabla formato wide que cuenta la cantidad de sentimientos
    que tuvo un usuario por día de cada tipo
    """
    return source.groupby([
            source['date'], var_name
        ]).size().unstack(fill_value=0)

def agregar_variables_desglosadas(source, map_variable):
    df_pie_chart = source.sum().reset_index(name='count')
    df_pie_chart['emotions_emoji'] = df_pie_chart[map_variable].map(emojis)
    return df_pie_chart
    
def calcular_sentimientos_para_usuarios(selected_users_messages):
    # Calculamos el resumen diario de cada usuario seleccionado
    emociones_diarios = {}
    sentimientos_diarios = {}
    for user, messages_user in selected_users_messages.items():
         # Quitamos los mensajes que están etiquetados como 'others'
        emociones = messages_user['emotions'] != 'others'
        emociones_diarios[str(user)] = desglosar_variable_por_dia(messages_user[emociones], 'emotions')
        
        sentimientos_diarios[str(user)] = desglosar_variable_por_dia(messages_user, 'sentiments')
        
    return emociones_diarios, sentimientos_diarios

def calcular_odio_diario(selected_users_messages):
    odio_diario = {}
    for user, messages_user in selected_users_messages.items():
        # Quitamos los mensajes que están etiquetados como ''
        odio = messages_user['odio'] != ''
        odio_diario[str(user)] = messages_user[odio].groupby([
            messages_user['date'], 'odio'
        ]).size().unstack(fill_value=0)
    return odio_diario

def serie_temporal(variables_diarios,  n_cols, smoothing=False):
    """
    - variables_diarios: un diccionario cuyas claves son los usuarios seleccionados
    y los valores son dataframes con las variables a mostrar en la serie temporal.
    - ncol: número de columnas a mostrar.
    """
    import altair as alt
    user0, variables_user0 = list(variables_diarios.items())[0]
    selected_users = list(variables_diarios.keys())
    variables = list(list(variables_diarios.values())[0].columns) # lista de las variables
    cols = st.columns(n_cols)
    for i, var in enumerate(variables):
        df_var = variables_user0[var].rename(str(user0))
        if len(selected_users)>1:
            # Como hay mas de un usuario seleccionado tenemos que unir para cada variable
            # el dataframe de los usuarios correspondientes  
            for user, variables_user in list(variables_diarios.items())[1:]:
                df_var_user = variables_user[var].rename(str(user))
                df_var = pd.merge(df_var, df_var_user, how='outer', left_index=True, right_index=True)
            # Cuando terminamos de unir el df_var tiene la variable correspondiente para todos los usuarios
        # Ponemos el dataframe en formato largo
        df_var = pd.melt(df_var.reset_index().fillna(0), id_vars=["date"], value_vars=selected_users, var_name="user")
        with cols[i%3]:
            st.subheader(f"{emojis[var]} {var}")

            date_range = (dt.date(2025, 6, 30), dt.date(2025, 7,5))

            # Create interval selection with initial value
            brush = alt.selection_interval(
                encodings=['x'],
                value={'x': date_range}
            )
            
            # Create base chart for both panels
            base = alt.Chart(df_var, width=600, height=200).mark_line(interpolate='monotone').encode(
                x = 'date:T',
                y = 'value:Q',
                color = 'user:N'
            )
            
            # Upper panel shows detailed view filtered by the brush
            upper = base.encode(
                alt.X('date:T').scale(domain=brush)
            )
            
            # Lower panel shows overview with the brush control
            lower = base.properties(
                height=60
            ).add_params(brush)
            
            # Combine the two charts
            chart = upper & lower

            st.altair_chart(chart, use_container_width=True)

def pie_chart(source, category, value, label_col):
    base = alt.Chart(source).encode(
        theta=alt.Theta(f"{value}:Q", stack=True),
        color=alt.Color(f"{category}:N") 
    )
    
    pie = base.mark_arc(innerRadius=50, outerRadius=150)
    
    text = base.mark_text(radius=120, size=30).encode(
        text=f"{label_col}:N" 
    )

    chart = pie + text
    return chart

def pie_chart2(source, category, value, label_col):
    # Agregamos el parámetro 'tooltip' en la base del gráfico
    base = alt.Chart(source).encode(
        theta=alt.Theta(f"{value}:Q", stack=True),
        color=alt.Color(f"{category}:N", legend=None),
        tooltip=[
            alt.Tooltip(f"{label_col}:N", title="Emoción"), # Muestra el emoji
            alt.Tooltip(f"{category}:N", title="Categoría"), # Muestra el nombre (opcional)
            alt.Tooltip(f"{value}:Q", title="Cantidad")      # Muestra el número exacto
        ]
    )
    
    # Mantenemos los radios definidos para centrar
    pie = base.mark_arc(innerRadius=50, outerRadius=150)
    
    # Mantenemos el texto centrado (radius=100)
    # text = base.mark_text(radius=100, size=30).encode(
    #     text=f"{label_col}:N" 
    # )
    
    chart = pie + text
    return chart


def bar_chart(source, category, value, var_title, label_col=None, color_map=None, category_on_y=True):
    """
    Dibuja un diagrama de barras en el que se muestra la categoria y el valor
    Opcionalmente se permite pasar un diccionario color_map para que cada categoria tenga su color
    en todos los gráficos. Ademas se permite poner un label_col que es el nombre de la columna de 
    labels que poner encima de cada barra.
    """
    if color_map:
        domain = list(color_map.keys())
        range_ = list(color_map.values())
        
        color_encoding = alt.Color(
            f"{category}:N", 
            scale=alt.Scale(domain=domain, range=range_), 
            legend=None
        )
    else:
        color_encoding = alt.Color(f"{category}:N", legend=None)

    if category_on_y == True:
        bars = alt.Chart(source).mark_bar(cornerRadiusBottomRight=5,cornerRadiusTopRight=5).encode(
            x=alt.X(f"{value}:Q", title="Cantidad"),
            y=alt.Y(f"{category}:N", sort='-x', title=var_title),
            color=color_encoding,
            tooltip=[
                alt.Tooltip(f"{value}:Q", title="Cantidad")
            ]
        )
        
    else: 
        # Si el gráfico esta de pie añadimos un poco de margen si hay emojis
        max_val = source[value].max()
        if label_col:
            escala = alt.Scale(domain=[0, max_val * 1.3]) # con un poco de margen añadido
        else:
            escala = alt.Scale(domain=[0, max_val]) # Sino hay emojis no hace falta margen
            
        bars = alt.Chart(source).mark_bar(cornerRadiusTopRight=5,cornerRadiusTopLeft=5).encode(
            x=alt.X(f"{category}:N", sort='-y',title=var_title),
            y=alt.Y(f"{value}:Q", title="Cantidad", scale=escala),
            color=color_encoding,
            tooltip=[
                alt.Tooltip(f"{value}:Q", title="Cantidad")
            ]
        )
        
    if label_col:
        if category_on_y:
            text = bars.mark_text(
                align='left',      
                baseline='middle', 
                dy=5,              
                size=30            
            ).encode(
                text=f"{label_col}:N"
            )
        else:
            text = bars.mark_text(
                align='center',      
                baseline='top', 
                dy=-30,              
                size=30            
            ).encode(
                text=f"{label_col}:N"
            )
        
        chart = (bars + text).properties(
            width=500, 
            height=alt.Step(40) 
        )
    else:
        chart = bars.properties(
            width=500, 
            height=alt.Step(40) 
        )
    
    return chart

def calcular_mayor_uso_palabra(source, pattern, regex=False, case=False):
    messages_with_pattern = source.loc[source['message'].str.contains(pattern, case=case, na=False, regex=regex), ['date', 'timestamp', 'author', 'message']]
    leaders = (
        messages_with_pattern
        .groupby('author')
        .count()['message']
        .sort_values(ascending=False)
        
        .reset_index()
    )
    coincidencias = str(leaders.head(1)['message'][0])
    name = str(leaders.head(1)['author'][0])
    return name, coincidencias

def calcular_insignias_palabras(source):
    insignias = {}

    for palabra in ["hola", "humo", "renta", "dinero fácil", "damaris", "nigga", "polla", "marina", "malisima", "nibba", "teta", "lino", "milf"]:
        name, coincidencias = calcular_mayor_uso_palabra(source, palabra)
        insignias[palabra] = {"ganador": name, "veces": coincidencias}

    return insignias
    
def calcular_insignia_relativa(df_categoria, nombre_insignia, insignias_dict, total_mensajes_autor):
    if not df_categoria.empty:
        # Mensajes por autor
        conteo_categoria = (
            df_categoria['author'].value_counts()
            .reindex(total_mensajes_autor.index, fill_value=0)
        )

        # Ajustamos los valores para que el que tenga menos no se vea beneficiado
        
        global_successes = conteo_categoria.sum() * 0.1
        global_total = total_mensajes_autor.sum() * 0.1
        global_failures = global_total - global_successes
        
        alpha_prior = global_successes + 1
        beta_prior = global_failures + 1
        
        alpha_post = conteo_categoria + alpha_prior
        beta_post = (total_mensajes_autor - conteo_categoria) + beta_prior        

        ratios = (alpha_post) / (alpha_post + beta_post) 
        
        ganador = ratios.idxmax()
        porcentaje = ratios.max() * 100
        
        veces = conteo_categoria[ganador] # Para saber cuántos mensajes reales fueron
        
        insignias_dict[nombre_insignia] = {
            "ganador": ganador, 
            "ratio": f"{porcentaje:.1f}%", 
            "veces": veces
        }

def calcular_insignia_palabras_relativas(df, regex, nombre_insignia, insignias_dict):
    mask = df['message'].str.contains(regex, case=False, na=False, regex=True)
    
    # 2. Agrupar por autor: sumar aciertos y contar total de mensajes
    stats = mask.groupby(df['author']).agg(exitos='sum', total='count')
    
    if stats['exitos'].any():
        # 3. Configuración Bayesiana (Laplace smoothing simple +1/+2)
        # Esto evita que 1/1 gane a 40/100
        stats['ratio_bayesiano'] = (stats['exitos'] + 1) / (stats['total'] + 2)
        
        ganador_id = stats['ratio_bayesiano'].idxmax()
        info_ganador = stats.loc[ganador_id]
        
        # Guardamos el porcentaje real (no el bayesiano) para mostrar, 
        # pero usamos el bayesiano para elegir al ganador
        porcentaje_real = (info_ganador['exitos'] / info_ganador['total']) * 100
        
        insignias_dict[nombre_insignia] = {
            "ganador": ganador_id,
            "ratio": f"{porcentaje_real:.1f}%",
            "veces": int(info_ganador['exitos'])
        }

# Ejemplo de uso:


def calcular_insignias_comportamiento(sentimientos, odio):
    insignias = {}
    total_mensajes_autor = sentimientos['author'].value_counts()
    total_mensajes_autor_odio = odio['author'].value_counts()
    
    # Mensaje con odio Hater🤬
    odio_df = odio[odio['odio'].isin(['hateful', 'targeted', 'aggresive'])]
    calcular_insignia_relativa(odio_df, "Hater 🤬", insignias, total_mensajes_autor_odio)

    # Mensajes con odio orientado
    odio_targeted = odio[odio['odio'] == 'targeted']
    calcular_insignia_relativa(odio_targeted, "Odia a las minorías 🏳️‍🌈⃠", insignias, total_mensajes_autor_odio)

    # Mensajes con odio agresivo
    odio_agresivo = odio[odio['odio'] == 'aggressive']
    calcular_insignia_relativa(odio_agresivo, "Agresivo 👊", insignias, total_mensajes_autor_odio)

    # Mensajes con tristeza
    sadness_df = sentimientos[sentimientos['emotions'] == 'sadness']
    calcular_insignia_relativa(sadness_df, "Tristón 😭", insignias, total_mensajes_autor)
    
    # Mensajes con miedo
    fear_df = sentimientos[sentimientos['emotions'] == 'fear']
    calcular_insignia_relativa(fear_df, "Cagón 😱", insignias, total_mensajes_autor)
    
    # Mensajes con felicidad ()
    felices_df = sentimientos[sentimientos['emotions'] == 'joy']
    calcular_insignia_relativa(felices_df, "Mr. Wonderful 🌈", insignias, total_mensajes_autor)

    # Mensajes con sorpresa
    sorpresa_df = sentimientos[sentimientos['emotions'] == 'surprise']
    calcular_insignia_relativa(sorpresa_df, "Fácil de sorprender 😯", insignias, total_mensajes_autor)

    # Mensajes optimistas
    optimista_df = sentimientos[sentimientos['sentiments'] == 'POS']
    calcular_insignia_relativa(optimista_df, "Todo va a salir bien 😊", insignias, total_mensajes_autor)

    # Mensajes pesimistas
    pesimista_df = sentimientos[sentimientos['sentiments'] == 'NEG']
    calcular_insignia_relativa(pesimista_df, "Todo va a salir mal 😩", insignias, total_mensajes_autor)

    # El que más mensajes ha enviado en total Yapper 🗣️
    conteo_total = sentimientos['author'].value_counts()
    if not conteo_total.empty:
        insignias["Yapper 🗣️"] = {"ganador": conteo_total.idxmax(), "veces": conteo_total.max()}

    # Mucho Texto 📜 y De pocas palabras 🤫
    promedio_palabras_df = sentimientos[['author', 'message']].copy()
    promedio_palabras_df['num_palabras'] = (
        promedio_palabras_df['message']
            .astype(str)
            .apply(lambda x: len(x.split()))
    )
    
    promedio_palabras = promedio_palabras_df.groupby('author')['num_palabras'].mean()
    if not promedio_palabras.empty:
        insignias["Mucho Texto 📜"] = {"ganador": promedio_palabras.idxmax(), "veces": round(promedio_palabras.max(), 1)}
        insignias["De pocas palabras 🤫"] = {"ganador": promedio_palabras.idxmin(), "veces": round(promedio_palabras.min(), 1)}

    # 5. Búho
    df_tiempo = sentimientos[['author', 'timestamp']].copy()
    
    df_tiempo['hora'] = pd.to_datetime(df_tiempo['timestamp'], format='mixed', errors='coerce').dt.hour
    
    madrugada_df = df_tiempo[(df_tiempo['hora'] >= 2) & (df_tiempo['hora'] < 6)]
    if not madrugada_df.empty:
        conteo_buho = madrugada_df['author'].value_counts()
        insignias["Señor de la noche 🌚"] = {"ganador": conteo_buho.idxmax(), "veces": conteo_buho.max()}
    
    regex_risa = 'jaj|😂|🤣'
    calcular_insignia_palabras_relativas(sentimientos, regex_risa, "Risueño 🤣", insignias)
    
    regex_mates = r'\b(matemáticas?|mates|topología|integral|derivada|álgebra|tfg)\b'
    calcular_insignia_palabras_relativas(sentimientos, regex_mates, "Friki 🧮", insignias)
    
    return insignias

def set_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://tu-imagen-aqui.jpg");
             background-attachment: fixed;
             background-size: cover;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

@st.cache_data
def mensajes_por_hora(df, columna_fecha='timestamp'):
    horas_serie = pd.to_datetime(df[columna_fecha]).dt.hour
    # Cuenta cuantos mensajes hay por hora
    counts = horas_serie.value_counts().reindex(range(24), fill_value=0).sort_index().reset_index() 
    counts.columns = ['hora', 'cantidad']
    
    return counts