import streamlit as st
import pandas as pd
import os
import psycopg2
from datetime import datetime
import hashlib

# Configuración de base de datos PostgreSQL
DATABASE_CONFIG = {
    'host': 'ep-nameless-dream-admzl0m7-pooler.c-2.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_i5su4fvBOwoK',
    'port': '5432',
    'sslmode': 'require'
}

def conectar_bd():
    """Conectar a la base de datos PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DATABASE_CONFIG['host'],
            database=DATABASE_CONFIG['database'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password'],
            port=DATABASE_CONFIG['port'],
            sslmode=DATABASE_CONFIG['sslmode']
        )
        return conn
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {str(e)}")
        return None

def crear_tabla():
    """Crear tabla si no existe"""
    try:
        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()
            
            # Crear tabla para almacenar las respuestas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluaciones (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    cedula VARCHAR(50) NOT NULL,
                    pregunta_id INTEGER NOT NULL,
                    pregunta TEXT NOT NULL,
                    opcion_seleccionada VARCHAR(500) NOT NULL,
                    opcion_correcta VARCHAR(500) NOT NULL,
                    es_correcta BOOLEAN NOT NULL,
                    fecha_evaluacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
    except Exception as e:
        st.error(f"Error creando tabla: {str(e)}")
        return False

def guardar_evaluacion_bd(nombre, cedula, respuestas_dict, preguntas_df):
    """Guardar evaluación en la base de datos"""
    try:
        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()
            
            for pregunta, respuesta_seleccionada in respuestas_dict.items():
                # Buscar la información de la pregunta
                pregunta_info = preguntas_df[preguntas_df['PREGUNTAS'] == pregunta].iloc[0]
                pregunta_id = pregunta_info['ID']
                respuesta_correcta = pregunta_info['RESPUESTA']
                es_correcta = respuesta_seleccionada == respuesta_correcta
                
                cursor.execute("""
                    INSERT INTO evaluaciones 
                    (nombre, cedula, pregunta_id, pregunta, opcion_seleccionada, opcion_correcta, es_correcta)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (nombre, cedula, pregunta_id, pregunta, respuesta_seleccionada, respuesta_correcta, es_correcta))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
    except Exception as e:
        st.error(f"Error guardando en base de datos: {str(e)}")
        return False

def calcular_puntaje(respuestas_dict, preguntas_df):
    """Calcular puntaje de la evaluación"""
    total_preguntas = len(respuestas_dict)
    respuestas_correctas = 0
    
    for pregunta, respuesta_seleccionada in respuestas_dict.items():
        pregunta_info = preguntas_df[preguntas_df['PREGUNTAS'] == pregunta].iloc[0]
        respuesta_correcta = pregunta_info['RESPUESTA']
        
        if respuesta_seleccionada == respuesta_correcta:
            respuestas_correctas += 1
    
    puntaje = respuestas_correctas
    porcentaje = (respuestas_correctas / total_preguntas) * 100
    
    return puntaje, porcentaje, respuestas_correctas, total_preguntas

@st.cache_data
def cargar_preguntas():
    """Cargar banco de preguntas"""
    try:
        df = pd.read_csv('Preguntas.csv', sep=';', encoding='latin1')
        
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        if 'ï»¿ID' in df.columns:
            df = df.rename(columns={'ï»¿ID': 'ID'})
        
        # Convertir la columna de opciones en listas
        df['OPCIONES_LISTA'] = df['OPCIONES'].apply(lambda x: [op.strip() for op in str(x).split(';')])
        return df
    except FileNotFoundError:
        st.error("No se encontró el archivo Preguntas.csv")
        return pd.DataFrame()

# Inicializar la tabla
crear_tabla()

# Inicializar el estado de la sesión
if 'preguntas_seleccionadas' not in st.session_state:
    df_preguntas = cargar_preguntas()
    if not df_preguntas.empty:
        st.session_state.preguntas_seleccionadas = df_preguntas.sample(n=min(10, len(df_preguntas))).reset_index(drop=True)
    else:
        st.session_state.preguntas_seleccionadas = pd.DataFrame()

if 'respuestas_enviadas' not in st.session_state:
    st.session_state.respuestas_enviadas = False

if 'datos_usuario' not in st.session_state:
    st.session_state.datos_usuario = {'nombre': '', 'cedula': ''}

# Interfaz principal
st.title("📝 Formulario de Evaluación")
st.markdown("---")

# Verificar si hay preguntas cargadas
if st.session_state.preguntas_seleccionadas.empty:
    st.error("No se pudieron cargar las preguntas. Verifica que el archivo 'Preguntas.csv' existe.")
else:
    if not st.session_state.respuestas_enviadas:
        # Formulario de datos del usuario
        st.markdown("### 👤 Información Personal")
        
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre completo:", value=st.session_state.datos_usuario['nombre'])
        with col2:
            cedula = st.text_input("Cédula:", value=st.session_state.datos_usuario['cedula'])
        
        # Actualizar datos en session_state
        st.session_state.datos_usuario['nombre'] = nombre
        st.session_state.datos_usuario['cedula'] = cedula
        
        # Validar que los datos del usuario estén completos
        datos_completos = nombre.strip() != '' and cedula.strip() != ''
        
        if not datos_completos:
            st.warning("⚠️ Por favor, complete su nombre y cédula para continuar.")
        
        st.markdown("---")
        
        # Mostrar información de la sesión
        st.info(f"📊 Preguntas seleccionadas para esta sesión: {len(st.session_state.preguntas_seleccionadas)}")
        
        respuestas = {}
        
        # Mostrar preguntas con sus opciones específicas
        for idx, row in st.session_state.preguntas_seleccionadas.iterrows():
            pregunta = row["PREGUNTAS"]
            opciones = row["OPCIONES_LISTA"]
            
            st.markdown(f"### Pregunta {idx + 1}")
            respuesta = st.selectbox(
                f"{pregunta}", 
                ['Selecciona una opción...'] + opciones, 
                key=f"pregunta_{idx}",
                disabled=not datos_completos
            )
            
            if respuesta != 'Selecciona una opción...':
                respuestas[pregunta] = respuesta
            
            st.markdown("---")
        
        # Validar que todas las preguntas estén respondidas
        total_preguntas = len(st.session_state.preguntas_seleccionadas)
        preguntas_respondidas = len(respuestas)
        
        # Mostrar progreso
        if datos_completos:
            progreso = preguntas_respondidas / total_preguntas
            st.progress(progreso)
            st.text(f"Progreso: {preguntas_respondidas}/{total_preguntas} preguntas respondidas")
        
        # Botones de acción
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔄 Generar Nuevas Preguntas"):
                df_preguntas = cargar_preguntas()
                if not df_preguntas.empty:
                    st.session_state.preguntas_seleccionadas = df_preguntas.sample(n=min(10, len(df_preguntas))).reset_index(drop=True)
                    st.rerun()
        
        with col3:
            enviar_habilitado = datos_completos and preguntas_respondidas == total_preguntas
            if st.button("📧 Enviar Respuestas", disabled=not enviar_habilitado):
                if enviar_habilitado:
                    # Guardar en base de datos
                    bd_guardado = guardar_evaluacion_bd(nombre, cedula, respuestas, st.session_state.preguntas_seleccionadas)
                    
                    if bd_guardado:
                        # Calcular puntaje
                        puntaje, porcentaje, correctas, total = calcular_puntaje(respuestas, st.session_state.preguntas_seleccionadas)
                        
                        st.session_state.puntaje_final = {
                            'puntaje': puntaje,
                            'porcentaje': porcentaje,
                            'correctas': correctas,
                            'total': total
                        }
                        
                        st.success("✅ ¡Respuestas enviadas correctamente!")
                        st.session_state.respuestas_enviadas = True
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar las respuestas. Inténtalo de nuevo.")
                else:
                    if not datos_completos:
                        st.error("Por favor, complete su nombre y cédula.")
                    else:
                        st.error("Por favor, responde todas las preguntas antes de enviar.")
        
        if datos_completos and not enviar_habilitado and preguntas_respondidas > 0:
            st.warning(f"⚠️ Faltan {total_preguntas - preguntas_respondidas} pregunta(s) por responder.")
    
    else:
        # Pantalla de confirmación con puntaje
        st.success("✅ **¡Formulario completado exitosamente!**")
        st.balloons()
        
        # Mostrar puntaje
        if 'puntaje_final' in st.session_state:
            puntaje_info = st.session_state.puntaje_final
            
            st.markdown("### 📊 Resultados de su evaluación")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Puntaje Total", f"{puntaje_info['puntaje']}/{puntaje_info['total']}")
            with col2:
                st.metric("Respuestas Correctas", puntaje_info['correctas'])
            with col3:
                st.metric("Porcentaje", f"{puntaje_info['porcentaje']:.1f}%")
            
            # Clasificación del rendimiento
            if puntaje_info['porcentaje'] >= 90:
                st.success("🏆 ¡Excelente rendimiento!")
            elif puntaje_info['porcentaje'] >= 80:
                st.success("👍 Muy buen rendimiento")
            elif puntaje_info['porcentaje'] >= 70:
                st.warning("⚠️ Rendimiento aceptable")
            else:
                st.error("📚 Se recomienda estudiar más")
        
        st.markdown("""
        ### ¡Gracias por completar la evaluación!
        
        ✅ Tus respuestas han sido guardadas en la base de datos  
        ✅ Tu puntaje ha sido calculado  
        ✅ Los datos están disponibles para análisis  
        """)

# Sidebar con información
with st.sidebar:
    st.header("ℹ️ Información")
    st.markdown("""
    **Instrucciones:**
    1. Complete su nombre y cédula
    2. Responda todas las preguntas
    3. Haga clic en 'Enviar Respuestas'
    4. Las respuestas se guardarán en la base de datos
    
    **Configuración:**
    - Archivo 'Preguntas.csv' en el directorio
    - Conexión a base de datos PostgreSQL configurada
    """)
    
    st.markdown("---")
    st.markdown("**Cada pregunta vale 1 punto**")
    st.markdown("**Puntaje máximo: 10 puntos**")
