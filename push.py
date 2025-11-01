import streamlit as st
from github import Github
from datetime import datetime
import pandas as pd
from io import StringIO
import requests
from PIL import Image
from io import BytesIO

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

    if st.button("Probar registro"):
        st.write("1️⃣ Iniciando conexión con GitHub...")
        
        try:
            # Conectar a GitHub
            g = Github(st.secrets["github_token"])
            repo = g.get_repo(st.secrets["github_repo"])
            st.success("✅ Conectado a GitHub exitosamente")
            
            # Buscar archivo
            st.write("2️⃣ Buscando archivo de registros...")
            try:
                contents = repo.get_contents("usage_log.csv")
                existing_data = contents.decoded_content.decode()
                df = pd.read_csv(StringIO(existing_data))
                st.success(f"✅ Archivo encontrado con {len(df)} registros")
                
                # Crear nuevo registro
                st.write("3️⃣ Añadiendo nuevo registro...")
                new_record = {
                    'ID': len(df) + 1,
                    'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'ASIN': asin1,
                    'ASIN.1': asin2,
                    'ASIN.2': asin3,
                    'Feedback': ''
                }
                
                df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
                
                # Guardar cambios
                st.write("4️⃣ Guardando cambios...")
                repo.update_file(
                    contents.path,
                    f"Update usage log - Test",
                    df.to_csv(index=False),
                    contents.sha
                )
                st.success("✅ Registro guardado exitosamente")
                st.balloons()
                
            except Exception as e:
                if "404" in str(e):
                    st.warning("⚠️ Archivo no encontrado, creando uno nuevo...")
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
                    st.success("✅ Nuevo archivo creado exitosamente")
                    st.balloons()
                else:
                    st.error(f"❌ Error accediendo al archivo: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Error de conexión: {str(e)}")

if __name__ == "__main__":
    main()