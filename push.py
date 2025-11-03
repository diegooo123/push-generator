import streamlit as st
from github import Github
from datetime import datetime
import pandas as pd
from io import StringIO
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import time

# Cache para almacenar imágenes
image_cache = {}

def get_amazon_image(asin):
    if asin in image_cache:
        return image_cache[asin]
        
    try:
        # Obtener imagen de la página de detalle
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        detail_url = f"https://www.amazon.com.mx/dp/{asin}"
        response = requests.get(detail_url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            img_element = soup.select_one('#landingImage, #imgBlkFront, #ebooksImgBlkFront, #main-image')
            
            if not img_element:
                img_element = soup.select_one('img.a-dynamic-image, img[data-a-dynamic-image]')
            
            if img_element:
                img_url = None
                for attr in ['src', 'data-old-hires', 'data-a-dynamic-image']:
                    if attr in img_element.attrs:
                        if attr == 'data-a-dynamic-image':
                            import json
                            urls = json.loads(img_element[attr])
                            if urls:
                                img_url = list(urls.keys())[0]
                        else:
                            img_url = img_element[attr]
                        break
                
                if img_url:
                    if not img_url.startswith('http'):
                        img_url = 'https:' + img_url
                    
                    img_response = requests.get(img_url, headers=headers)
                    if img_response.status_code == 200:
                        img = Image.open(BytesIO(img_response.content))
                        image_cache[asin] = img
                        return img
        
        return None
    except Exception as e:
        print(f"Error getting image for ASIN {asin}: {str(e)}")
        return None

def create_notification_image(asins, sizes, background_color='#FFFFFF', final_size=(634, 300)):
    bg_color = tuple(int(background_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    background = Image.new('RGB', final_size, bg_color)
    
    margin = int(final_size[0] * 0.05)
    vertical_margin = int(final_size[1] * 0.1)
    
    num_images = len(asins)
    if num_images == 1:
        book_width = int(final_size[0] * sizes[0])
        positions = [int(final_size[0]/2 - book_width/2)]
        book_widths = [book_width]
    elif num_images == 2:
        book_width_1 = int(final_size[0] * sizes[0])
        book_width_2 = int(final_size[0] * sizes[1])
        spacing = int(final_size[0] * 0.1)
        total_width = book_width_1 + book_width_2 + spacing
        start_x = int((final_size[0] - total_width) / 2)
        positions = [
            start_x,
            start_x + book_width_1 + spacing
        ]
        book_widths = [book_width_1, book_width_2]
    else:
        book_widths = [int(final_size[0] * size) for size in sizes[:3]]
        spacing = int((final_size[0] - sum(book_widths)) / 4)
        positions = [
            spacing,
            spacing * 2 + book_widths[0],
            spacing * 3 + book_widths[0] + book_widths[1]
        ]
    
    book_height = int(final_size[1] - (2 * vertical_margin))
    
    for i, asin in enumerate(asins):
        if i < 3 and asin.strip():
            book = get_amazon_image(asin)
            if book:
                current_width = book_widths[i]
                original_ratio = book.width / book.height
                new_height = min(book_height, int(current_width / original_ratio))
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
            time.sleep(1)
    
    return background

def save_to_github(asin1, asin2, asin3):
    try:
        g = Github(st.secrets["github_token"])
        repo = g.get_repo(st.secrets["github_repo"])
        
        try:
            contents = repo.get_contents("usage_log.csv")
            existing_data = contents.decoded_content.decode()
            df = pd.read_csv(StringIO(existing_data))
            
            new_record = {
                'ID': len(df) + 1,
                'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ASIN': asin1,
                'ASIN.1': asin2,
                'ASIN.2': asin3,
                'Feedback': ''
            }
            
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            
            repo.update_file(
                contents.path,
                f"Update usage log - Test",
                df.to_csv(index=False),
                contents.sha
            )
            return True
            
        except Exception as e:
            if "404" in str(e):
                df = pd.DataFrame([{
                    'ID': 1,
                    'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'ASIN': asin1,
                    'ASIN.1': asin2,
                    'ASIN.2': asin3,
                    'Feedback': ''
                }])
                
                repo.create_file(
                    "usage_log.csv",
                    "Create usage log",
                    df.to_csv(index=False)
                )
                return True
            else:
                return False
    
    except Exception as e:
        return False

def main():
    st.title("Generador de Imágenes Push")
    st.write("Ingresa hasta 3 ASINs")

    # Estilo personalizado para los controles
    st.markdown("""
        <style>
        /* Estilo para la barra del slider (fondo negro) */
        .stSlider > div > div > div {
            background-color: #000000 !important;
        }
        
        /* Estilo para el thumb del slider (círculo blanco) */
        .stSlider > div > div > div > div > div {
            background-color: #FFFFFF !important;
            border: 2px solid #000000 !important;
        }
        
        /* Estilo para el valor del slider */
        .stSlider > div > div > div > div > div > div {
            color: #000000 !important;
        }
        
        /* Estilo para el track activo del slider */
        .stSlider > div > div > div[data-baseweb="slider"] > div[data-testid="stTickBar"] > div {
            background: #FF9900 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        asin1 = st.text_input("ASIN 1:", help="Ingresa el primer ASIN", key="asin1")
        size1 = st.slider("Tamaño imagen 1", 0.1, 0.6, 0.25, 0.05, help="Ajusta el tamaño relativo", key="size1")
    with col2:
        asin2 = st.text_input("ASIN 2:", help="Ingresa el segundo ASIN (opcional)", key="asin2")
        size2 = st.slider("Tamaño imagen 2", 0.1, 0.6, 0.25, 0.05, help="Ajusta el tamaño relativo", key="size2")
    with col3:
        asin3 = st.text_input("ASIN 3:", help="Ingresa el tercer ASIN (opcional)", key="asin3")
        size3 = st.slider("Tamaño imagen 3", 0.1, 0.6, 0.25, 0.05, help="Ajusta el tamaño relativo", key="size3")

    background_color = st.color_picker(
        "Color de fondo",
        "#FFFFFF",
        help="Selecciona el color de fondo",
        key="bg_color"
    )

    # Enlace de feedback
    st.markdown("<div style='text-align: right;'><a href='mailto:ddig@amazon.com?subject=Feedback%20-%20Generador%20de%20Imágenes%20Push' style='color: #FF9900;'>📧 Send feedback</a></div>", unsafe_allow_html=True)

    asins = [asin for asin in [asin1, asin2, asin3] if asin.strip()]
    sizes = [size1, size2, size3]

    if asins:
        with st.spinner('Generando imagen...'):
            image = create_notification_image(asins, sizes, background_color)
        
        st.image(image, caption="Vista previa", use_container_width=True)
        
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=95)
        img_byte_arr.seek(0)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Validar y Descargar", 
                        help="Valida y guarda la imagen generada",
                        type="primary"):
                if save_to_github(asin1, asin2, asin3):
                    st.success("✅ Validación exitosa")
                    img_byte_arr.seek(0)
                    with col2:
                        st.download_button(
                            label="⬇️ Descargar imagen",
                            data=img_byte_arr,
                            file_name=f"push_notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                            mime="image/jpeg",
                            key="download_after_save",
                            type="primary"
                        )
                else:
                    st.error("❌ Error en la validación")

if __name__ == "__main__":
    main()