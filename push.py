import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
from datetime import datetime

class ImageProcessor:
    def __init__(self):
        pass

    def get_amazon_image(self, asin):
        try:
            url = f"https://images-na.ssl-images-amazon.com/images/P/{asin}.01.LZZZZZZZ.jpg"
            response = requests.get(url)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
            return None
        except Exception as e:
            st.error(f"Error al procesar ASIN {asin}: {e}")
            return None

    def create_notification_image(self, asins, background_color='#FFFFFF', final_size=(634, 300)):
        # Convertir color hex a RGB
        bg_color = tuple(int(background_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        background = Image.new('RGB', final_size, bg_color)
        
        # Configuración base
        margin = int(final_size[0] * 0.05)  # 5% de margen
        vertical_margin = int(final_size[1] * 0.1)  # 10% de margen vertical
        
        # Calcular dimensiones según número de imágenes
        num_images = len(asins)
        if num_images == 1:
            # Una imagen centrada
            book_width = int(final_size[0] * 0.25)  # 40% del ancho total
            positions = [int(final_size[0]/2 - book_width/2)]  # Centrado
        elif num_images == 2:
            # Dos imágenes centradas
            book_width = int(final_size[0] * 0.25)  # 30% del ancho para cada imagen
            spacing = int(final_size[0] * 0.2)  # 15% de espacio entre ellas
            total_width = (2 * book_width) + spacing
            start_x = int((final_size[0] - total_width) / 2)
            positions = [
                start_x,
                start_x + book_width + spacing
            ]
        else:
            # Tres imágenes distribuidas
            book_width = int((final_size[0] - (2 * margin)) / 3.5)
            spacing = int((final_size[0] - (3 * book_width)) / 4)
            positions = [
                spacing,
                spacing * 2 + book_width,
                spacing * 3 + book_width * 2
            ]
        
        book_height = int(final_size[1] - (2 * vertical_margin))
        
        # Procesar cada imagen
        for i, asin in enumerate(asins):
            if i < 3 and asin.strip():
                book = self.get_amazon_image(asin)
                if book:
                    # Mantener proporción
                    original_ratio = book.width / book.height
                    new_height = min(book_height, int(book_width / original_ratio))
                    new_width = int(new_height * original_ratio)
                    
                    # Redimensionar
                    book = book.resize(
                        (new_width, new_height),
                        Image.Resampling.LANCZOS
                    )
                    
                    # Centrar verticalmente
                    y_position = int((final_size[1] - new_height) / 2)
                    
                    # Pegar imagen
                    background.paste(
                        book,
                        (positions[i], y_position)
                    )
        
        return background

def main():
    st.title("Generador de Imágenes Push")
    st.write("Ingresa hasta 3 ASINs")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        asin1 = st.text_input("ASIN 1:", help="Ingresa el primer ASIN")
    with col2:
        asin2 = st.text_input("ASIN 2:", help="Ingresa el segundo ASIN (opcional)")
    with col3:
        asin3 = st.text_input("ASIN 3:", help="Ingresa el tercer ASIN (opcional)")

    background_color = st.color_picker(
        "Color de fondo",
        "#FFFFFF",
        help="Selecciona el color de fondo"
    )

    if st.button("Generar imagen"):
        if not asin1 and not asin2 and not asin3:
            st.error("Por favor, ingresa al menos un ASIN")
            return

        with st.spinner("Procesando..."):
            processor = ImageProcessor()
            asins = [asin for asin in [asin1, asin2, asin3] if asin.strip()]
            image = processor.create_notification_image(asins, background_color)

            # Mostrar preview
            st.image(image, caption="Vista previa", use_container_width=True)
            
            # Preparar imagen para descarga
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=95)
            img_byte_arr.seek(0)
            
            # Botón de descarga
            st.download_button(
                label="Descargar imagen",
                data=img_byte_arr,
                file_name=f"push_notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                mime="image/jpeg"
            )

if __name__ == "__main__":
    main()
