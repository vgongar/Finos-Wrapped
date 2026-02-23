import streamlit as st
from DataLoader import DataLoader
import streamlit_authenticator as stauth
import time
import io # Para gestionar binarios
import pandas as pd
import copy


_LOREM_IPSUM = """
Bienvenido al *Wrapped de los finos*. A través de las múltiples páginas podrás explorar la interacción de cada usuario, los más destacados y explorar el vocabulario a lo largo del tiempo.

Te recomiendo que visites la página de 🌍 Estadísticas globales primero y utilices los links para visitar los perfiles de los chavales. Podrás descubrir las insignias de cada uno y ver cuál tienes tu (si es que tienes 🥲).

Espero poder ampliar la página con más funcionalidades, insignias y estadísticas. ¡Espero que la disfrutes! 

Aún no hay una enciclopedia de insgnias pero puedes imaginarte lo que significan la mayoría. También añadiré una de esas.

Si tienes alguna sugerencia mándame un mensaje... ¡O usa el grupo!
"""

def stream_data():
    for word in _LOREM_IPSUM.split(" "):
        yield word + " "
        time.sleep(0.02)



credentials = copy.deepcopy(st.secrets["credentials"].to_dict())

authenticator = stauth.Authenticate(
    credentials,
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days']
)
    
authenticator.login(location='main')

authentication_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")
username = st.session_state.get("username")

if authentication_status:
    st.title(f"🚀 Bienvenido, {name}")
    
    if "datos_cargados" not in st.session_state:
        st.session_state["datos_cargados"] = False
    if not st.session_state["datos_cargados"]:
        dataloader = DataLoader("finos-wrapped")
        # Modificamos la cache
        for key, value in dataloader.cache.items():
                st.session_state[key] = value
        st.session_state["datos_cargados"] = True
        
    st.write_stream(stream_data)
    
    #st.write(list(st.session_state.keys()))
elif authentication_status == False:
    st.error('Contraseña incorrecta')
elif authentication_status == None:
    st.info('Por favor, introduce la contraseña del grupo para continuar.')

        