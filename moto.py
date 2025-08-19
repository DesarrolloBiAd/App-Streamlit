import streamlit as st
import pandas as pd
import os

# Cargar banco de preguntas con encabezado manual
@st.cache_data
def cargar_preguntas():
    # Usar ruta relativa al archivo actual
    ruta_archivo = os.path.join(os.path.dirname(__file__), "Preguntas.csv")
    
    # Si no existe, buscar en el directorio actual
    if not os.path.exists(ruta_archivo):
        ruta_archivo = "Preguntas.csv"
    
    df = pd.read_csv(
        ruta_archivo,
        sep=';', header=None, names=['ID', 'Pregunta', 'Opciones'], encoding='latin1'
    )
    # Convertir la columna de opciones en listas
    df['Opciones'] = df['Opciones'].apply(lambda x: [op.strip() for op in str(x).split(';')])
    return df


df_preguntas = cargar_preguntas()

# Seleccionar 10 preguntas aleatorias
preguntas_aleatorias = df_preguntas.sample(n=10)

st.title("Formulario de Evaluación Aleatoria")

respuestas = {}

# Mostrar preguntas con sus opciones específicas
for i, row in preguntas_aleatorias.iterrows():
    pregunta = row["Pregunta"]
    opciones = row["Opciones"]
    respuesta = st.selectbox(f"{i+1}. {pregunta}", opciones, key=i)
    respuestas[pregunta] = respuesta

# Botón para enviar
if st.button("Enviar respuestas"):
    df_respuestas = pd.DataFrame([respuestas])
    df_respuestas.to_csv("respuestas.csv", mode='a', index=False, header=False)
    st.success("¡Respuestas enviadas correctamente!")
 