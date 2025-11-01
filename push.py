import streamlit as st
from github import Github
from datetime import datetime
import pandas as pd
from io import StringIO

def main():
    st.title("Test de Registro en GitHub")
    
    # Entrada simple de un ASIN
    asin = st.text_input("Ingresa un ASIN de prueba:", value="8417880569")
    
    if st.button("Probar registro real"):
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
                df = pd.read_csv(StringIO(exististing_data))
                st.success(f"✅ Archivo encontrado con {len(df)} registros")
                
                # Crear nuevo ro registro
                st.write("3️⃣ Añadiendo nuevo registro...")
                new_record = {
                    'ID': len(df) + 1,
                    'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'ASIN': asin,
                    'ASIN.1': '',
                    'ASIN.2': '',
                    'Feedback': 'Test de registro'
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
                
            except Exception as e:
                if "404" in str(e):
                    st.warning("⚠️ Archivo no encontrado, creando uno nuevo...")
                    df = pd.DataFrame([{
                        'ID': 1,
                        'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'ASIN': asin,
                        'ASIN.1': '',
                        'ASIN.2': '',
                        'Feedback': 'Primer registro'
                    }])
                    
                    repo.create_file(
                        "usage_log.csv",
                        "Create usage log",
                        df.to_csv(index=False)
                    )
                    st.success("✅ Nuevo archivo creado exitosamente")
                else:
                    st.error(f"❌ Error accediendo al archivo: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Error de conexión: {str(e)}")

if __name__ == "__main__":
    main()