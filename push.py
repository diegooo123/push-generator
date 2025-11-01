import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
from datetime import datetime
import pandas as pd

def log_usage(asins, feedback=""):
    """Registra el uso en un CSV"""
    try:
        # Crear o cargar el archivo de registro
        log_file = "usage_log.csv"
        if os.path.exists(log_file):
            df = pd.read_csv(log_file)
        else:
            df = pd.DataFrame(columns=['Fecha', 'ASIN1', 'ASIN2', 'ASIN3', 'Feedback'])
        
        # Crear nuevo registro
        new_record = {
            'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ASIN1': asins[0] if len(asins) > 0 else '',
            'ASIN2': asins[1] if len(asins) > 1 else '',
            'ASIN3': asins[2] if len(asins) > 2 else '',
            'Feedback': feedback
        }
        
        # Añadir al DataFrame y guardar
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        df.to_csv(log_file, index=False)
    except:
        pass

# [El resto del código se mantiene igual hasta la parte del botón de descarga]

        if st.download_button(
            label="Descargar imagen",
            data=img_byte_arr,
            file_name=f"push_notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
            mime="image/jpeg"
        ):
            log_usage(asins)  # Registrar uso al descargar

    feedback = st.text_area(
        "Feedback (opcional)",
        help="Comparte tu experiencia o sugerencias",
        key="feedback"
    )

    if feedback and st.button("Guardar feedback"):
        log_usage(asins, feedback)  # Registrar uso con feedback