import streamlit as st
from PIL import Image
import requests
from io import BytesIO, StringIO
from datetime import datetime
from github import Github
import pandas as pd
import time

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
            return None

    def create_notification_image(self, asins, background_color='#FFFFFF', final_size=(634, 300)):
        bg_color = tuple(int(background_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        background = Image.new('RGB', final_size, bg_color)
        
        margin = int(final_size[0] * 0.05)
        vertical_margin = int(final_size[1] * 0.1)
        
        num_images = len(asins)
        if num_imagesges == 1:
            book_width = int(final_size[0] * 0.4)
            positions = [int(final_size[0]/2 - book_width/2)]
        elif num_images == 2:
            book_width = int(final_size[0] * 0.25)
            spacing = int(final_size[0] * 0.2)
            total_width = (2 * book_width) + spacing
            start_x = int((final_size[0] - total_width) / 2)
            positions = [
                start_x,
                start_x + book_width + spacing
            ]
        else:
            book_width = int((final_size[0] - (2 * margin)) / 3.5)
            spacing = int((final_size[0] - (3 * book_width)) / 4)
            positions = [
                spacing,
                spacing * 2 + book_width,
                spacing * 3 + book_width * 2
            ]
        
        book_height = int(final_size[1] - (2 * vertical_margin))
        
        for i, asin in enumerate(asins):
            if i < 3 and asin.strip():
                book = self.get_amazon_image(asin)
                if book:
                    original_ratio = book.width / book.height
                    new_height = min(book_height, int(book_width / original_ratio))
                    new_width = int(new_height * original_ratio)
                    
                    book = book.resize(
                        (new_width, new_height),
                        Image.Resampling.LANCZOS
                    )
                    
                    y_position = int((final_size[1] - new_height) / 2)
                    
                    background.paste(
                        book,
                        (positions[i], y_position)
                    )
        
        return background

def register_usage_silently(asins):
    debug_container = st.empty()
    try:
        debug_container.write("🚀 Iniciando registro...")
        
        g = Github(st.secrets["github_token"])
        repo = g.get_repo(st.secrets["github_repo"])
        debug_container.write("✅ Conexión a GitHub OK")
        
        try:
            contents = repo.get_contents("usage_log.csv")
            existing_data = contents.decoded_content.decode()
            df = pd.read_csv(StringIO(existing_data))
            debug_container.write(f"📁 Archivo encontrado con {len(df)} registros")
            
            new_record = {
                'ID': len(df) + 1,
                'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ASIN': asins[0] if len(asins) > 0 else '',
                'ASIN.1': asins[1] if len(asins) > 1 else '',
                'ASIN.2': asins[2] if len(asins) > 2 else '',
                'Feedback': ''
            }
            debug_container.write(f"📝 Nuevo registro: {new_record}")
            
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            update = repo.update_file(
                contents.path,
                f"Update usage log",
                df.to_csv(index=False),
                contents.sha
            )
            debug_container.write("✨ Archivo actualizado exitosamente")
            
        except Exception as e:
            if "404" in str(e):
                debug_container.write("📁 Creando nuevo archivo...")
                df = pd.DataFrame([{
                    'ID': 1,
                    'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'ASIN': asins[0] if len(asins) > 0 else '',
                    'ASIN.1': asins[1] if len(asins) > 1 else '',
                    'ASIN.2': asins[2] if len(asins) > 2 else '',
                    'Feedback': ''
                }])
                
                repo.create_file(
                    "usage_log.csv",
                    "Create usage log",
                    df.to_csv(index=False)
                )
                debug_container.write("✅ Nuevo archivo creado exitosamente")
            else:
                debug_container.write(f"❌ Error al procesar archivo: {str(e)}")
            
    except Exception as e:
        debug_container.write(f"❌ Error de conexión: {str(e)}")
    
    # Esperar un momento para que los mensajes sean visibles
    time.sleep(2)
    # Limpiar los mensajes de debug
    debug_container.empty()

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
        
        if st.download_button(
            label="Descargar imagen",
            data=img_byte_arr,
            file_name=f"push_notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
            mime="image/jpeg"
        ):
            register_usage_silently(asins)
            st.balloons()

if __name__ == "__main__":
    main()