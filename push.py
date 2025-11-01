import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
from datetime import datetime
import pandas as pd
import json

class ExcelTracker:
    def __init__(self):
        self.file_path = "usage_tracker.csv"  # Cambiamos a CSV para mayor compatibilidad
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            df = pd.DataFrame(columns=['ID', 'Fecha', 'ASIN', 'ASIN.1', 'ASIN.2', 'Feedback'])
            df.to_csv(self.file_path, index=False)
    
    def add_record(self, asins, feedback=""):
        try:
            df = pd.read_csv(self.file_path) if os.path.exists(self.file_path) else pd.DataFrame(columns=['ID', 'Fecha', 'ASIN', 'ASIN.1', 'ASIN.2', 'Feedback'])
            new_record = {
                'ID': len(df) + 1,
                'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ASIN': asins[0] if len(asins) > 0 else '',
                'ASIN.1': asins[1] if len(asins) > 1 else '',
                'ASIN.2': asins[2] if len(asins) > 2 else '',
                'Feedback': feedback
            }
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            df.to_csv(self.file_path, index=False)
            return True
        except Exception as e:
            return False

# [El resto de las clases ImageProcessor se mantiene igual]

d

def register_download(asins):
    tracker = ExcelTracker()
    tracker.add_record(asins)

def main():
    st.title("Generador de Imágenes Push")
    st.write("Ingresa hasta 3 ASINs")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        asin1 = st.text_input("ASIN 1:", help="Ingresa el primer ASIN", key="asin1")
    with col2:
        asin2 = st.text_input("ASIN 2:", help="Ingresa el segundo ASIN (opcional)", key="asin2")
    with col3:
        asin3 = st.text_input("ASIN 3:", help="Ingresa el tercer ASIN (opcional)", key="asin3")

    background_color = st.color_picker(
        "Color de fondo",
        "#FFFFFF",
        help="Selecciona el color de fondo",
        key="bg_color"
    )

    asins = [asin for asin in [asin1, asin2, asin3] if asin.strip()]

    if asins:
        processor = ImageProcessor()
        image = processor.create_notification_image(asins, background_color)
        st.image(image, caption="Vista previa", use_container_width=True)
        
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=95)
        img_byte_arr.seek(0)
        
        st.download_button(
            label="Descargar imagen",
            data=img_byte_arr,
            file_name=f"push_notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
            mime="image/jpeg",
            on_click=lambda: register_download(asins)
        )

    feedback = st.text_area(
        "Feedback (opcional)",
        help="Comparte tu experiencia o sugerencias",
        key="feedback"
    )

    if feedback:
        if st.button("Guardar feedback"):
            tracker = ExcelTracker()
            tracker.add_record(asins, feedback)

if __name__ == "__main__":
    main()

    