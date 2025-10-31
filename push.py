import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import os
from datetime import datetime
import time

class ImageProcessor:
    def __init__(self, images_folder="temp_images"):
        self.images_folder = images_folder
        self.ensure_images_folder()
        
    def ensure_images_folder(self):
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)

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

    def create_notification_image(self, asins, final_size=(634, 300)):
        background = Image.new('RGB', final_size, 'white')
        
        margin = int(final_size[0] * 0.05)
        vertical_margin = int(final_size[1] * 0.1)
        available_width = final_size[0] - (2 * margin)
        spacing = int(available_width * 0.1 / 2)
        
        book_width = int((available_width - (2 * spacing)) / 3)
        book_height = int(final_size[1] - (2 * vertical_margin))
        
        positions = [
            margin,
            margin + book_width + spacing,
            margin + (2 * (book_width + spacing))
        ]
        
        for i, asin in enumerate(asins):
            if i < 3 and asin.strip():  # Verificar que el ASIN no esté vacío
                with st.status(f"Procesando ASIN: {asin}"):
                    book = self.get_amazon_image(asin)
                    
                    if book:
                        original_ratio = book.width / book.height
                        new_height = min(book_height, int(book_width / original_ratio))
                        new_width = int(new_height * original_ratio)
                        
                        book = book.resize(
                            (new_width, new_height),
                            Image.Resampling.LANCZOS
                        )
                        
                        y_offset = (book_height - new_height) // 2
                        x_offset = (book_width - new_width) // 2
                        
                        background.paste(
                            book,
                            (positions[i] + x_offset, vertical_margin + y_offset)
                        )
        
        # Guardar imagen
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"{self.images_folder}/notification_{timestamp}.jpg"
        background.save(output_path, 'JPEG', quality=95, optimize=True)
        return output_path

def main():
    st.title("Generador de Imágenes Push Amazon")
    st.write("Crea imágenes para push notifications con portadas de libros de Amazon")

    # Crear contenedor para el formulario
    with st.form("push_form"):
        # Campo para email
        email = st.text_input("Email para recibir la imagen:", 
                             help="Ingresa tu correo electrónico donde recibirás la imagen")
        
        # Campos para ASINs
        st.subheader("Ingresa los ASINs de los libros (máximo 3)")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            asin1 = st.text_input("ASIN 1:", 
                                 help="Ingresa el ASIN del primer libro")
        with col2:
            asin2 = st.text_input("ASIN 2:", 
                                 help="Ingresa el ASIN del segundo libro (opcional)")
        with col3:
            asin3 = st.text_input("ASIN 3:", 
                                 help="Ingresa el ASIN del tercer libro (opcional)")

        # Botón de envío
        submitted = st.form_submit_button("Generar Imagen")

    if submitted:
        if not asin1:
            st.error("Por favor, ingresa al menos un ASIN")
            return
        
        if not email:
            st.error("Por favor, ingresa un correo electrónico")
            return

        # Procesar la solicitud
        with st.spinner("Generando imagen..."):
            processor = ImageProcessor()
            asins = [asin for asin in [asin1, asin2, asin3] if asin.strip()]
            
            try:
                image_path = processor.create_notification_image(asins)
                
                # Mostrar la imagen generada
                st.success("¡Imagen generada exitosamente!")
                st.image(image_path, caption="Vista previa de la imagen")
                
                # Botón para descargar la imagen
                with open(image_path, "rb") as file:
                    btn = st.download_button(
                        label="Descargar imagen",
                        data=file,
                        file_name=f"push_notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                        mime="image/jpeg"
                    )
                
                # Aquí podrías agregar el código para enviar por email
                st.info(f"Se enviará la imagen al correo: {email}")
                
            except Exception as e:
                st.error(f"Error al generar la imagen: {e}")

if __name__ == "__main__":
    main()