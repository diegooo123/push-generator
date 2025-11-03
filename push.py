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
import json

# Cache para almacenar imágenes
image_cache = {}

def get_amazon_image(asin, max_retries=3):
    if asin in image_cache:
        return image_cache[asin]
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    for attempt in range(max_retries):
        try:
            detail_url = f"https://www.amazon.com.mx/dp/{asin}"
            response = requests.get(detail_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                selectors = [
                    '#landingImage',
                    '#imgBlkFront',
                    '#ebooksImgBlkFront',
                    '#main-image',
                    'img.a-dynamic-image',
                    '#imageBlock_feature_div img',
                    '#img-canvas img',
                    '#imageBlock img'
                ]
                
                for selector in selectors:
                    img_element = soup.select_one(selector)
                    if img_element:
                        for attr in ['data-a-dynamic-image', 'data-old-hires', 'src']:
                            img_url = None
                            if attr in img_element.attrs:
                                if attr == 'data-a-dynamic-image':
                                    try:
                                        urls = json.loads(img_element[attr])
                                        if urls:
                                            img_url = max(urls.items(), key=lambda x: sum(map(int, x[1])))[0]
                                    except:
                                        continue
                                else:
                                    img_url = img_element[attr]
                                
                                if img_url:
                                    if not img_url.startswith('http'):
                                        img_url = 'https:' + img_url
                                    
                                    try:
                                        img_response = requests.get(img_url, headers=headers, timeout=10)
                                        if img_response.status_code == 200:
                                            img = Image.open(BytesIO(img_response.content))
                                            if img.size[0] > 100 and img.size[1] > 100:
                                                image_cache[asin] = img
                                                return img
                                    except:
                                        continue
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Intento {attempt + 1} fallido para ASIN {asin}: {str(e)}")
            time.sleep(1)
            continue
    
    print(f"No se pudo obtener la imagen para el ASIN {asin} después de {max_retries} intentos")
    return None

def create_notification_image(asins, sizes, background_color='#FFFFFF', final_size=(634, 300)):
    bg_color = tuple(int(background_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    background = Image.new('RGB', final_size, bg_color)
    
    max_attempts = 5
    for attempt in range(max_attempts):
        success = True
        images = []
        
        for asin in asins:
            if not asin.strip():
                continue
                
            img = get_amazon_image(asin)
            if img is None:
                success = False
                break
            images.append(img)
        
        if success and len(images) == len([a for a in asins if a.strip()]):
            break
            
        if attempt < max_attempts - 1:
            time.sleep(2)
            print(f"Reintentando obtener imágenes (intento {attempt + 2}/{max_attempts})")
    
    margin = int(final_size[0] * 0.05)
    vertical_margin = int(final_size[1] * 0.1)
    
    num_images = len(images)
    if num_images == 0:
        return background
        
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
        positions = [start_x, start_x + book_width_1 + spacing]
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
    
    for i, img in enumerate(images):
        if i < 3:
            current_width = book_widths[i]
            original_ratio = img.width / img.height
            new_height = min(book_height, int(current_width / original_ratio))
            new_width = int(new_height * original_ratio)
            
            img = img.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )
            
            y_position = int((final_size[1] - new_height) / 2)
            
            background.paste(
                img,
                (positions[i], y_position)
            )
    
    return background

def save_to_github(asin1, asin2, asin3):
    try:
        # Verificar si las credenciales están configuradas
        if "github_token" not in st.secrets:
            raise Exception("Token de GitHub no configurado en los secretos")
        if "github_repo" not in st.secrets:
            raise Exception("Repositorio de GitHub no configurado en los secretos")

        # Inicializar GitHub
        g = Github(st.secrets["github_token"])
        
        try:
            repo = g.get_repo(st.secrets["github_repo"])
        except Exception as e:
            raise Exception(f"Error al acceder al repositorio: {str(e)}")
        
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
            
            try:
                repo.update_file(
                    contents.path,
                    f"Update usage log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    df.to_csv(index=False),
                    contents.sha
                )
                return True, "Archivo actualizado correctamente"
            except Exception as e:
                raise Exception(f"Error al actualizar el archivo: {str(e)}")
            
        except Exception as e:
            if "404" in str(e):
                try:
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
                    return True, "Nuevo archivo creado correctamente"
                except Exception as e:
                    raise Exception(f"Error al crear el archivo: {str(e)}")
            else:
                raise Exception(f"Error al leer el archivo existente: {str(e)}")
    
    except Exception as e:
        return False, str(e)

def main():
    st.title("Generador de Imágenes Push")
    st.write("Ingresa hasta 3 ASINs")

    # Estilo personalizado para los controles
    st.markdown("""
        <style>
        .stSlider > div > div > div {
            background-color: #000000 !important;
        }
        
        .stSlider > div > div > div > div > div {
            background-color: #FFFFFF !important;
            border: 2px solid #000000 !important;
        }
        
        .stSlider > div > div > div > div > div > div {
            color: #000000 !important;
        }
        
        .stSlider > div > div > div[data-baseweb="slider"] > div[data-testid="stTickBar"] > div {
            background: #FF9900 !important;
        }

        .stTextInput input {
            background-color: #ffd9b3 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    st.write("Tamaño")
    
    with col1:
        asin1 = st.text_input("ASIN 1", key="asin1")
        size1 = st.slider("1", 0.1, 0.6, 0.25, 0.05, key="size1")
    with col2:
        asin2 = st.text_input("ASIN 2", key="asin2")
        size2 = st.slider("2", 0.1, 0.6, 0.25, 0.05, key="size2")
    with col3:
        asin3 = st.text_input("ASIN 3", key="asin3")
        size3 = st.slider("3", 0.1, 0.6, 0.25, 0.05, key="size3")

    background_color = st.color_picker(
        "Color de fondo",
        "#FFFFFF",
        key="bg_color"
    )

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
            if st.button("Descargar", 
                        type="primary"):
                success, message = save_to_github(asin1, asin2, asin3)
                if success:
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
                    st.error(f"❌ Error en la validación: {message}")
                    st.error("Por favor, verifica las credenciales de GitHub y los permisos del repositorio.")

if __name__ == "__main__":
    main()