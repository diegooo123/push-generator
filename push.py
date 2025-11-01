import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
from datetime import datetime
import pandas as pd
from github import Github
from io import StringIO

def log_usage(asins, feedback=""):
    try:
        # Conectar a GitHub
        g = Github(st.secrets["github_token"])
        repo = g.get_repo(st.secrets["github_repo"])
        
        # Intentar obtener el archivo existente
        try:
            contents = repo.get_contents("usage_log.csv")
            existing_data = contents.decoded_content.decode()
            df = pd.read_csv(StringIO(existing_data))
        except:
            # Si el archivo no existe, crear uno nuevo
            df = pd.DataFrame(columns=['ID', 'Fecha', 'ASIN', 'ASIN.1', 'ASIN.2', 'Feedback'])
        
        # Añadir nuevo registro
        new_record = {
            'ID': len(df) + 1,
            'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ASIN': asins[0] if len(asins) > 0 else '',
            'ASIN.1': asins[1] if len(asins) > 1 else '',
            'ASIN.2': asins[2] if len(asins) > 2 else '',
            'Feedback': feedback
        }
        
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        
        # Guardar cambios en GitHub
        if 'contents' in locals():
            repo.update_file(
                contents.path,
                f"Update usage log",
                df.to_csv(index=False),
                contents.sha
            )
        else:
            repo.create_file(
                "usage_log.csv",
                "Create usage log",
                df.to_csv(index=False)
            )
    except Exception as e:
        print(f"Error logging usage: {e}")

# [El resto del código se mantiene igual]
