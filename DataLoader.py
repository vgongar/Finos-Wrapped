from google.cloud import storage
import pandas as pd
import streamlit as st
import io
from utils import users_names

class DataLoader:
    def __init__(self, bucket_name: str) -> dict:
        """
        Se conecta al bucket de Google Cloud y carga los archivos en un diccionario.
        """
        self.cache = {}
        
        creds_dict = dict(st.secrets["gcp_service_account"])
        client = storage.Client.from_service_account_info(creds_dict)
        
        bucket = client.bucket(bucket_name)
        files = client.list_blobs(bucket_name)
        
        for file in files:
            name = file.name
            
            with st.spinner(f"Cargando {name}..."):
                # Si el archivo es el _chat.txt
                if name.endswith('.txt'):
                    self.cache[name] = file.download_as_text()
                elif name.endswith('.csv'):
    # Si el archivo es csv lo parseamos y lo ponemos como dataframe
                    binary_data = file.download_as_bytes()
                    df = pd.read_csv(
                        io.BytesIO(binary_data),
                        encoding='utf-8',
                        header=0,
                        parse_dates=['timestamp']
                    )
                    """
                    Esto debería hacerse antes de subir el archivo.
                    Eso hay que arreglarlo
                    """
                    # Borramos los mensajes Fino
                    df = df[~df['author'].str.contains("=")]
                    
                    # Cambiamos los nombres
                    df['author'] = df['author'].map(users_names)
                    
                    # Extraemos la fecha y la hora
                    df["date"] = df.timestamp.dt.date
                    df["time"] = df.timestamp.dt.time
                    
                    
                    self.cache[name] = df
            
                else:
                    self.cache[name] = file.download_as_bytes()
        else:
            st.success("¡Datos descargados!")
            st.balloons()