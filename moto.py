import streamlit as st
import pandas as pd
import os
from datetime import datetime
from supabase import create_client, Client

# Configuración de Supabase
SUPABASE_CONFIG = {
    'url': "https://iixjbkmpasbordjuairl.supabase.co",
    'key': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlpeGpia21wYXNib3JkanVhaXJsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIyNDg0MDMsImV4cCI6MjA2NzgyNDQwM30.gSsGtX6hp6lR50oMTZrh2rhEAXGtMVgRN2mL84u2LNU"
}

def crear_conexion_supabase():
    """Crear conexión a Supabase"""
    try:
        supabase: Client = create_client(SUPABASE_CONFIG['url'], SUPABASE_CONFIG['key'])
        return supabase
    except Exception as e:
        st.error(f"Error al conectar con Supabase: {str(e)}")
        return None

# Cargar banco de preguntas con manejo de errores robusto
@st.cache_data
def cargar_preguntas():
    """Carga las preguntas desde Excel con manejo robusto de errores"""
    # Usar ruta relativa al archivo actual
    ruta_archivo = os.path.join(os.path.dirname(__file__), "Preguntas.xlsx")
    
    # Si no existe, buscar en el directorio actual
    if not os.path.exists(ruta_archivo):
        ruta_archivo = "Preguntas.xlsx"
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            st.error("❌ No se encontró el archivo 'Preguntas.xlsx'. Por favor, asegúrate de que existe en el directorio.")
            return pd.DataFrame()
        
        # Leer el archivo Excel
        df = pd.read_excel(ruta_archivo, engine='openpyxl', header=0)
        
        # # Mostrar las columnas disponibles para debug
        # st.write("📋 Columnas encontradas en el Excel:", list(df.columns))
        
        # Normalizar nombres de columnas (eliminar espacios y convertir a mayúsculas)
        df.columns = df.columns.str.strip().str.upper()
        
        # Verificar que las columnas necesarias existan
        columnas_requeridas = []
        
        # Verificar columna ID
        if 'ID' not in df.columns:
            columnas_requeridas.append('ID')
        
        # Verificar columna de preguntas
        if 'PREGUNTAS' not in df.columns and 'PREGUNTA' in df.columns:
            df.rename(columns={'PREGUNTA': 'PREGUNTAS'}, inplace=True)
        
        # Verificar columna de opciones
        if 'OPCIONES' not in df.columns and 'OPCION' in df.columns:
            df.rename(columns={'OPCION': 'OPCIONES'}, inplace=True)
            
        if 'PREGUNTAS' not in df.columns:
            columnas_requeridas.append('PREGUNTAS (o PREGUNTA)')
        if 'OPCIONES' not in df.columns:
            columnas_requeridas.append('OPCIONES (o OPCION)')
        
        if columnas_requeridas:
            st.error(f"❌ Faltan las siguientes columnas en el Excel: {', '.join(columnas_requeridas)}")
            st.info("💡 Las columnas disponibles son: " + ', '.join(df.columns.tolist()))
            return pd.DataFrame()
        
        # Procesar la columna de opciones
        if 'OPCIONES' in df.columns:
            def procesar_opciones(x):
                if pd.isna(x):
                    return ['Opción A', 'Opción B', 'Opción C', 'Opción D']  # Opciones por defecto
                return [op.strip() for op in str(x).split(';') if op.strip()]
            
            df['OPCIONES'] = df['OPCIONES'].apply(procesar_opciones)
        
        # Eliminar filas vacías
        df = df.dropna(subset=['PREGUNTAS'])
        
        if len(df) == 0:
            st.error("❌ No se encontraron preguntas válidas en el archivo Excel.")
            return pd.DataFrame()
        
        st.success(f"✅ Se cargaron {len(df)} preguntas correctamente")
        return df
        
    except ImportError as e:
        if "openpyxl" in str(e):
            st.error("❌ Falta la librería 'openpyxl'. Ejecuta: pip install openpyxl")
        else:
            st.error(f"❌ Error de importación: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo Excel: {str(e)}")
        st.info("💡 Verifica que el archivo 'Preguntas.xlsx' tenga las columnas: ID, PREGUNTAS, OPCIONES")
        return pd.DataFrame()

def guardar_respuestas_supabase(nombre, cedula, respuestas_dict, preguntas_df, puntaje_total, calificacion_final):
    """Función para guardar las respuestas en Supabase"""
    try:
        supabase = crear_conexion_supabase()
        if not supabase:
            return False
        
        fecha_evaluacion = datetime.now().isoformat()
        registros_exitosos = 0
        
        # Guardar cada respuesta como un registro separado
        for pregunta, respuesta_seleccionada in respuestas_dict.items():
            # Encontrar la pregunta en el DataFrame original para obtener ID y respuesta correcta
            try:
                fila_pregunta = preguntas_df[preguntas_df['PREGUNTAS'] == pregunta].iloc[0]
                
                # Convertir int64 de pandas a int nativo de Python
                pregunta_id_original = int(fila_pregunta['ID']) if pd.notna(fila_pregunta['ID']) else None
                respuesta_correcta = str(fila_pregunta.get('RESPUESTA', respuesta_seleccionada))
                es_correcta = respuesta_seleccionada == respuesta_correcta
                
            except (IndexError, KeyError):
                pregunta_id_original = None
                respuesta_correcta = str(respuesta_seleccionada)
                es_correcta = True  # Si no hay respuesta correcta definida, asumimos que es correcta
            
            registro = {
                'nombre': str(nombre),
                'cedula': str(cedula),
                'pregunta_id': pregunta_id_original,
                'pregunta': str(pregunta),
                'opcion_seleccionada': str(respuesta_seleccionada),
                'opcion_correcta': respuesta_correcta,
                'es_correcta': bool(es_correcta),
                'Calificacion': int(puntaje_total),  # ← CORREGIDO: Con mayúscula
                'fecha_evaluacion': fecha_evaluacion
            }
            
            try:
                response = supabase.table("Preguntas motorola").insert(registro).execute()
                if response.data:
                    registros_exitosos += 1
                else:
                    st.error(f"Error al insertar pregunta con ID {pregunta_id_original}: No se recibieron datos")
                    
            except Exception as e:
                st.error(f"Error al guardar pregunta con ID {pregunta_id_original}: {str(e)}")
                # Mostrar el registro para debug
                st.write("Registro que causó el error:", registro)
        
        return registros_exitosos == len(respuestas_dict)
        
    except Exception as e:
        st.error(f"Error general al guardar en Supabase: {str(e)}")
        return False

def calcular_puntaje_y_calificacion(respuestas_dict, preguntas_df):
    """Calcular el puntaje y la calificación basada en las respuestas correctas"""
    puntaje = 0
    total_preguntas = len(respuestas_dict)
    
    for pregunta, respuesta_seleccionada in respuestas_dict.items():
        # Buscar la pregunta en el DataFrame original
        try:
            fila_pregunta = preguntas_df[preguntas_df['PREGUNTAS'] == pregunta].iloc[0]
            if 'RESPUESTA' in fila_pregunta and pd.notna(fila_pregunta['RESPUESTA']):
                respuesta_correcta = fila_pregunta['RESPUESTA']
                if respuesta_seleccionada == respuesta_correcta:
                    puntaje += 1
            else:
                # Si no hay respuesta correcta definida, asumimos que es correcta
                puntaje += 1
        except (IndexError, KeyError):
            # Si no se encuentra la pregunta, no sumar punto
            continue
    
    # Calcular calificación sobre 5.0 (escala colombiana típica)
    calificacion = (puntaje / total_preguntas)
    
    return puntaje, round(calificacion, 2)

def obtener_interpretacion_calificacion(calificacion):
    """Obtener interpretación de la calificación"""
    if calificacion >= 4.5:
        return "🌟 **¡Excelente trabajo!** Tu desempeño ha sido sobresaliente.", "success"
    elif calificacion >= 4.0:
        return "👍 **¡Muy buen trabajo!** Tu desempeño ha sido muy satisfactorio.", "success"
    elif calificacion >= 3.5:
        return "✅ **¡Buen trabajo!** Tu desempeño ha sido satisfactorio.", "info"
    elif calificacion >= 3.0:
        return "⚠️ **Desempeño regular.** Hay áreas de mejora.", "warning"
    else:
        return "📚 **Se recomienda estudiar más.** Es importante reforzar los conocimientos.", "error"

# Inicializar el estado de la sesión
if 'preguntas_seleccionadas' not in st.session_state:
    st.session_state.preguntas_seleccionadas = pd.DataFrame()
    st.session_state.preguntas_cargadas = False

if 'respuestas_enviadas' not in st.session_state:
    st.session_state.respuestas_enviadas = False

if 'puntaje_final' not in st.session_state:
    st.session_state.puntaje_final = 0

if 'calificacion_final' not in st.session_state:
    st.session_state.calificacion_final = 0.0

# Interfaz principal
st.title("📝 Formulario de Evaluación")
st.markdown("---")

# Cargar preguntas si no se han cargado
if not st.session_state.preguntas_cargadas:
    with st.spinner("Cargando preguntas..."):
        df_preguntas = cargar_preguntas()
        if not df_preguntas.empty:
            st.session_state.preguntas_seleccionadas = df_preguntas.sample(n=min(10, len(df_preguntas))).reset_index(drop=True)
            st.session_state.preguntas_cargadas = True
        else:
            st.session_state.preguntas_seleccionadas = pd.DataFrame()

# Verificar si hay preguntas cargadas
if st.session_state.preguntas_seleccionadas.empty:
    st.error("❌ No se pudieron cargar las preguntas.")
    st.info("🔧 Soluciones posibles:")
    st.markdown("""
    1. **Verifica que existe el archivo 'Preguntas.xlsx'** en el directorio
    2. **Instala openpyxl**: `pip install openpyxl`
    3. **Verifica las columnas del Excel**:
       - Debe tener una columna llamada 'ID'
       - Debe tener una columna llamada 'PREGUNTAS' o 'PREGUNTA'
       - Debe tener una columna llamada 'OPCIONES' o 'OPCION'
    4. **Opcional**: Columna 'RESPUESTA' para el cálculo de puntaje
    """)
    
    if st.button("🔄 Intentar cargar de nuevo"):
        st.session_state.preguntas_cargadas = False
        st.rerun()
        
else:
    # Mostrar información de la sesión
    st.info(f"📊 Preguntas seleccionadas para esta sesión: {len(st.session_state.preguntas_seleccionadas)}")
    
    if not st.session_state.respuestas_enviadas:
        # Campos de información personal
        st.markdown("## 👤 Información Personal")
        
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            nombre = st.text_input("📝 Nombre completo*", key="nombre_usuario")
        
        with col_info2:
            cedula = st.text_input("🆔 Número de cédula*", key="cedula_usuario")
        
        st.markdown("---")
        
        # Validar información personal
        info_personal_completa = bool(nombre.strip() and cedula.strip())
        
        if not info_personal_completa:
            st.warning("⚠️ Por favor, completa tu información personal antes de continuar con las preguntas.")
        
        respuestas = {}
        
        # Mostrar preguntas con sus opciones específicas (solo si la info personal está completa)
        if info_personal_completa:
            st.markdown("## 📋 Preguntas de Evaluación")
            
            for idx, row in st.session_state.preguntas_seleccionadas.iterrows():
                pregunta = row["PREGUNTAS"]
                opciones = row["OPCIONES"]
                pregunta_id = row["ID"]
                
                st.markdown(f"### Pregunta {idx + 1} (ID: {pregunta_id})")
                respuesta = st.selectbox(
                    f"{pregunta}", 
                    ['Selecciona una opción...'] + opciones, 
                    key=f"pregunta_{idx}"
                )
                
                if respuesta != 'Selecciona una opción...':
                    respuestas[pregunta] = respuesta
                
                st.markdown("---")
        
        # Validar que todas las preguntas estén respondidas
        total_preguntas = len(st.session_state.preguntas_seleccionadas)
        preguntas_respondidas = len(respuestas)
        
        if info_personal_completa:
            # Mostrar progreso
            progreso = preguntas_respondidas / total_preguntas if total_preguntas > 0 else 0
            st.progress(progreso)
            st.text(f"Progreso: {preguntas_respondidas}/{total_preguntas} preguntas respondidas")
        
        # Botones de acción
        col2, col3 = st.columns([1, 1])
        
        # with col1:
        #     if st.button("🔄 Generar Nuevas Preguntas"):
        #         st.session_state.preguntas_cargadas = False
        #         st.session_state.respuestas_enviadas = False
        #         st.rerun()
        
        with col3:
            enviar_habilitado = info_personal_completa and preguntas_respondidas == total_preguntas
            if st.button("💾 Guardar Respuestas", disabled=not enviar_habilitado):
                if enviar_habilitado:
                    with st.spinner("Guardando respuestas..."):
                        # Calcular puntaje y calificación
                        puntaje, calificacion = calcular_puntaje_y_calificacion(respuestas, st.session_state.preguntas_seleccionadas)
                        st.session_state.puntaje_final = puntaje
                        st.session_state.calificacion_final = calificacion
                        
                        # Guardar en Supabase
                        guardado_exitoso = guardar_respuestas_supabase(
                            nombre, 
                            cedula, 
                            respuestas, 
                            st.session_state.preguntas_seleccionadas,
                            puntaje,
                            calificacion
                        )
                        
                        if guardado_exitoso:
                            st.success("✅ ¡Respuestas guardadas correctamente en la base de datos!")
                            st.session_state.respuestas_enviadas = True
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar las respuestas. Inténtalo de nuevo.")
                else:
                    if not info_personal_completa:
                        st.error("Por favor, completa tu información personal.")
                    else:
                        st.error("Por favor, responde todas las preguntas antes de guardar.")
        
        if info_personal_completa and not enviar_habilitado and preguntas_respondidas > 0:
            st.warning(f"⚠️ Faltan {total_preguntas - preguntas_respondidas} pregunta(s) por responder.")
    
    else:
        # Pantalla de confirmación con puntaje
        st.success("✅ **¡Formulario completado exitosamente!**")
        st.balloons()

        # Mostrar puntaje
        st.markdown("## 🏆 Resultados de la Evaluación")
        col_resultado = st.columns(1)[0]
        with col_resultado:
            st.markdown(f"""
            <div style="
                background: linear-gradient(90deg, #4CAF50, #45a049);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                color: white;
                margin: 20px 0;
            ">
                <h3 style="margin: 0; color: white;">Puntaje</h3>
                <h1 style="margin: 10px 0; font-size: 2.5em; color: white;">{st.session_state.puntaje_final}/10</h1>
                <p style="margin: 0; font-size: 1.1em; color: white;">
                    {(st.session_state.puntaje_final/10)*100:.0f}% correctas
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        ### ¡Gracias por completar la evaluación!
        ✅ Tus respuestas han sido guardadas en la base de datos  
        ✅ Tu puntaje ha sido registrado  
        ✅ Los datos están disponibles para análisis  
        """)

# Sidebar con información
with st.sidebar:
    st.header("ℹ️ Información")
    st.markdown("""
    **Instrucciones:**
    1. Completa tu información personal
    2. Responde todas las preguntas (10 preguntas)
    3. Haz clic en 'Guardar Respuestas'
    4. Ve tu puntaje y calificación final
    
    **Sistema de Puntuación:**
    - Cada pregunta correcta = 1 punto
    - Puntaje máximo = 10 puntos
    - Calificación sobre 5.0 (escala colombiana)
    """)
    
    # Mostrar estadísticas de la sesión
    if st.session_state.respuestas_enviadas:
        st.markdown("---")
        st.markdown("### 📊 Estadísticas")
        st.metric("Puntaje Final", f"{st.session_state.puntaje_final}/10")
        # st.metric("Calificación", f"{st.session_state.calificacion_final}/5.0")
        st.metric("Porcentaje", f"{(st.session_state.puntaje_final/10)*100:.0f}%")
    