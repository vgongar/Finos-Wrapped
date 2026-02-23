import re
import os


def generar_mensaje(fila):
    autor = fila['author']
    texto = fila['message']
    fecha = fila['date']
    hora = fila['timestamp'].strftime('%H:%M')

    div = f"""
    <div class='msg sent'>
        <div class='metadata'>{autor}</div>
        <span class='text'>{texto}</span>
        <span class='time'>{fecha} {hora}</span>
    </div>
    """
    return div
    

def generar_html_whatsapp(df_messages, theme,max_width="500px"):
    """
    Convierte un dataframe de WhatsApp Parser en un string html para streamlit.
    """

    
    
    # Paletas de colores
    es_oscuro = theme is not None and theme.get("base") == "dark"

    if es_oscuro:
        colores = {
            "bg_body": "#0b141a",       # Fondo exterior
            "bg_chat": "#0b141a",       # Fondo del contenedor
            "bg_msg": "#005c4b",        # Verde oscuro WhatsApp
            "text_main": "#e9edef",     # Texto casi blanco
            "text_time": "#8696a0",     # Gris tenue para la hora
            "text_author": "#d395e0",   # Violeta claro para el nombre
            "border": "#222d34"         # Borde sutil
        }
    else:
        colores = {
            "bg_body": "#e5ddd5",
            "bg_chat": "#e5ddd5",
            "bg_msg": "#dcf8c6",
            "text_main": "#000000",
            "text_time": "rgba(0,0,0,0.45)",
            "text_author": "#572364",
            "border": "whitesmoke"
        }

    html_header = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='UTF-8'>
        <style>
            body {{
                font-family: 'Segoe UI', Helvetica, Arial;
                background-color: {colores['bg_body']};
                padding: 20px;
                color: {colores['text_main']};
            }}
            .chat {{
                margin: auto;
                display: flex;
                flex-direction: column;
                height: 500px;
                max-width: {max_width};
                overflow-y: auto;
                background-color: {colores['bg_chat']};
                padding: 10px;
                border: 1px solid {colores['border']};
                border-radius: 8px;
            }}
            .msg {{
                padding: 7px 10px;
                margin-bottom: 4px;
                border-radius: 7px;
                max-width: 85%;
                position: relative;
                font-size: 14px;
                box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);
                background-color: {colores['bg_msg']};
                align-self: flex-end; /* Asumimos 'sent' por defecto */
                border-top-right-radius: 0;
            }}
            .text {{
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            .time {{
                font-size: 10px;
                color: {colores['text_time']};
                float: right;
                margin: 4px 0 -2px 8px;
            }}
            .metadata {{
                color: {colores['text_author']};
                font-weight: bold;
                font-size: 12px;
                margin-bottom: 3px;
            }}
        </style>
    </head>
    <body><div class='chat'>
    """

    df_messages['html'] = df_messages.apply(generar_mensaje, axis = 1)
            
    cuerpo_chat = df_messages['html'].str.cat(sep='\n')

    # Concatenamos el principio y el final
    html_final = html_header + cuerpo_chat + "\n</div></body></html>"
    
    
    return html_final

