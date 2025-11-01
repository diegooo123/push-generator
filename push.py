import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime

def main():
    st.title("Test de Mensajes")
    
    # Entrada simple de un ASIN
    asin = st.text_input("Ingresa un ASIN de prueba:", value="8417880569")
    
    if st.button("Probar registro"):
        st.write("1️⃣ Iniciando prueba...")
        
        # Simular pasos del registro
        with st.spinner("Conectando..."):
            st.success("✅ Paso 1: Conexión exitosa")
            st.write("---")
           
        with st.spinner("Buscando archivo..."):
            st.info("📁 Archivo de registros encontrado")
            st.write("---")
        
        with st.spinner("Guardando registro..."):
            st.success(f"✅ Registro guardado para ASIN: {asin}")
            st.write("---")
        
        st.balloons()

if __name__ == "__main__":
    main()