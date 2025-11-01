import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime

def test_dependencies():
    """Función para probar las dependencias una por una"""
    st.write("Probando dependencias...")
    
    # Probar PIL
    try:
        st.write("1. Probando PIL...")
        img = Image.new('RGB', (100, 100), 'white')
        st.image(img)
        st.success("✅ PIL funciona correctamente")
    except Exception as e:
        st.error(f"❌ Error en PIL: {e}")

    # Probar requests
    try:
        st.write("2. Probando requests...")
        response = requests.get("https://www.amazon.com")
        st.success("✅ Requests funciona correctamente")
    except Exception as e:
        st.error(f"❌ Error en requests: {e}")

    # Probar GitHub
    try:
        st.write("3. Probando GitHub...")
        from github import Github
        g = Github(st.secrets["github_token"])
        repo = g.get_repo(st.secrets["github_repo"])
        st.success("✅ GitHub funciona correctamente")
        st.write(f"Repositorio conectado: {st.secrets['github_repo']}")
    except Exception as e:
        st.error(f"❌ Error en GitHub: {e}")

def main():
    st.title("Diagnóstico del Generador de Imágenes Push")
    
    # Botón para probar dependencias
    if st.button("Probar Dependencias"):
        test_dependencies()
    
    st.divider()
    
    # Interfaz básica
    st.write("Prueba básica de generación de imagen")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        asin1 = st.text_input("ASIN 1 (prueba):", value="8417880569")
    with col2:
        asin2 = st.text_input("ASIN 2 (opcional):", value="")
    with col3:
        asin3 = st.text_input("ASIN 3 (opcional):", value="")

    if st.button("Probar Generación"):
        asins = [asin for asin in [asin1, asin2, asin3] if asin.strip()]
        
        for asin in asins:
            try:
                st.write(f"Probando ASIN: {asin}")
                url = f"https://images-na.ssl-images-amazon.com/images/P/{asin}.01.LZZZZZZZ.jpg"
                response = requests.get(url)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    st.image(image, caption=f"Imagen para ASIN: {asin}")
                    st.success(f"✅ Imagen descargada correctamente para ASIN {asin}")
                else:
                    st.error(f"❌ No se pudo descargar la imagen para ASIN {asin}")
            except Exception as e:
                st.error(f"❌ Error procesando ASIN {asin}: {e}")

    st.divider()
    
    # Probar registro
    st.write("Prueba de registro")
    if st.button("Probar Registro"):
        try:
            from github import Github
            g = Github(st.secrets["github_token"])
            repo = g.get_repo(st.secrets["github_repo"])
            
            test_content = f"Test registro {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            try:
                # Intentar actualizar archivo existente
                contents = repo.get_contents("test_log.txt")
                repo.update_file(
                    contents.path,
                    "Update test log",
                    test_content,
                    contents.sha
                )
            except:
                # Si no existe, crear nuevo archivo
                repo.create_file(
                    "test_log.txt",
                    "Create test log",
                    test_content
                )
            
            st.success("✅ Prueba de registro exitosa")
        except Exception as e:
            st.error(f"❌ Error en prueba de registro: {e}")

if __name__ == "__main__":
    main()
