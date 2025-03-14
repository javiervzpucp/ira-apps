# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 11:46:15 2025

@author: jveraz
"""

# -*- coding: utf-8 -*-
"""
App de Streamlit para Conversión Archivística - Versión Cloud
"""

import streamlit as st  # Framework principal
import pandas as pd     # Manipulación de datos
import os               # Manejo de sistema de archivos
import io               # Manejo de buffers de memoria
import tempfile         # Directorios temporales
from ira_atom_v2 import ISADConverter  # Lógica de conversión
from langchain_huggingface import HuggingFaceEndpoint
from langchain.schema import HumanMessage

# Configuración inicial
st.set_page_config(
    page_title="Conversor ISAD(G)", 
    page_icon="📚",
    layout="wide",
    menu_items={
        'About': "Herramienta desarrollada para el Archivo Histórico Riva-Agüero PUCP"
    }
)

def main():
    # Título de la aplicación
    st.title("🖋️ Conversor de Documentos Archivísticos a ISAD(G)")
    st.markdown("---")

    # Sidebar para configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Manejo del token en cloud y local
        if 'HF_API_TOKEN' in st.secrets:
            hf_token = st.secrets.HF_API_TOKEN
            st.success("Token de Hugging Face detectado")
        else:
            hf_token = st.text_input("Ingrese su Token de Hugging Face", type="password")
            st.markdown("[Obtener token](https://huggingface.co/settings/tokens)")
        
        st.markdown("---")
        st.info("""
        **Instrucciones:**
        1. Sube tu archivo CSV
        2. Espera el procesamiento
        3. Descarga los resultados
        """)

    # Componente principal
    uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

    if uploaded_file and hf_token:
        os.environ["HF_API_TOKEN"] = hf_token
        
        try:
            converter = ISADConverter()
            
            with st.spinner("Procesando con IA..."):
                # Usar archivos temporales en memoria
                with tempfile.TemporaryDirectory() as tmp_dir:
                    # Procesar desde memoria
                    input_path = os.path.join(tmp_dir, "input.csv")
                    with open(input_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    output_base = os.path.join(tmp_dir, "output")
                    
                    if converter.process(input_path, output_base):
                        # Leer resultados
                        csv_path = f"{output_base}.csv"
                        excel_path = f"{output_base}.xlsx"
                        
                        # Mostrar vista previa
                        st.subheader("📄 Vista Previa de los Resultados")
                        preview_df = pd.read_csv(csv_path)
                        st.dataframe(preview_df.head(), use_container_width=True)
                        
                        # Botones de descarga
                        col1, col2 = st.columns(2)
                        
                        with col1:  # CSV
                            with open(csv_path, "rb") as f:
                                st.download_button(
                                    label="⬇️ Descargar CSV",
                                    data=f.read(),
                                    file_name="resultados_isad.csv",
                                    mime="text/csv"
                                )
                        
                        with col2:  # Excel
                            with open(excel_path, "rb") as f:
                                st.download_button(
                                    label="⬇️ Descargar Excel",
                                    data=f.read(),
                                    file_name="resultados_isad.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                    
                    else:
                        st.error("Error en el procesamiento. Verifica el formato del archivo.")
        
        except Exception as e:
            st.error(f"🚨 Error crítico: {str(e)}")
            st.stop()

    else:
        # Mensaje inicial
        st.markdown("""
        ### 📋 Formato Requerido
        Tu CSV debe contener estas columnas:
        - `Signatura` (requerido)
        - `Fecha cronica` (formato flexible)
        - `Institucion`  
        - `Categoria`  
        - `Pais`  
        - `Observaciones`
        
        ---
        ### 🛠️ Características
        - Conversión automática a estándar ISAD(G)
        - Mejora de metadatos con IA
        - Generación de CSV y Excel
        - Compatible con documentos históricos
        """)

if __name__ == "__main__":
    main()