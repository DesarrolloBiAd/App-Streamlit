import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from supabase import create_client, Client
import time
import random
import asyncio
import threading

# Configuración de página (debe ser lo primero)
st.set_page_config(
    page_title="Evaluación Motorola",
    page_icon="https://p3-ofp.static.pub//fes/cms/2025/01/16/7aiyjr6t3hszpzvsfnbwip54i0ovkz395647.png",
    layout="wide"
)

# CSS adaptativo para tema claro y oscuro
def obtener_estilo_tema():
    """Retorna los estilos CSS adaptativos para tema claro y oscuro"""
    return """
    <style>
    .card-adaptive {
        background-color: var(--background-color);
        color: var(--text-color);
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 4px rgba(0, 0, 0, var(--shadow-opacity));
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .timer-card {
        background-color: var(--timer-bg);
        color: var(--text-color);
        border-left: 5px solid #1f77b4;
        text-align: center;
    }
    
    .timer-card-warning {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        color: #856404;
    }
    
    .timer-card-danger {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        color: #721c24;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .question-card {
        background-color: var(--card-bg);
        color: var(--text-color);
        border-left: 5px solid #007bff;
        font-size: 24px;
        font-weight: bold;
        line-height: 1.3;
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: normal;
        max-width: 100%;
        padding: 20px;
    }
    
    .logo-container {
        background-color: var(--background-color);
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 8px rgba(0, 0, 0, var(--shadow-opacity));
        padding: 10px;
        border-radius: 15px;
        display: inline-block;
    }
    
    .logo-container img {
        display: block;
        filter: var(--logo-filter);
    }
    
    .gradient-card {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white !important;
        margin: 20px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .gradient-card h1, .gradient-card h2, .gradient-card h3, .gradient-card p {
        color: white !important;
        margin: 5px 0;
    }
    
    /* Variables por defecto (tema claro) */
    :root {
        --background-color: white;
        --border-color: #e0e0e0;
        --text-color: #000000;
        --card-bg: #f8f9fa;
        --timer-bg: #f0f2f6;
        --shadow-opacity: 0.1;
        --logo-filter: none;
    }
    
    /* Tema oscuro automático */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #262730;
            --border-color: #404040;
            --text-color: #ffffff;
            --card-bg: #1e1e1e;
            --timer-bg: #2d2d2d;
            --shadow-opacity: 0.3;
            --logo-filter: brightness(0) invert(1);
        }
    }
    
    /* Streamlit tema oscuro */
    .stApp[data-theme="dark"] {
        --background-color: #0e1117;
        --border-color: #404040;
        --text-color: #ffffff;
        --card-bg: #262730;
        --timer-bg: #1e1e1e;
        --shadow-opacity: 0.3;
        --logo-filter: brightness(0) invert(1);
    }
    
    .stApp[data-theme="light"] {
        --background-color: white;
        --border-color: #e0e0e0;
        --text-color: #000000;
        --card-bg: #f8f9fa;
        --timer-bg: #f0f2f6;
        --shadow-opacity: 0.1;
        --logo-filter: none;
    }
    
    /* Estilos adicionales para mejor apariencia */
    .info-success {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 5px solid #4CAF50;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .info-warning {
        background-color: rgba(255, 193, 7, 0.1);
        border-left: 5px solid #FFC107;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .info-error {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 5px solid #F44336;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .auto-refresh {
        position: fixed;
        top: 10px;
        right: 10px;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
        z-index: 1000;
    }
    </style>
    """

# Aplicar estilos CSS
st.markdown(obtener_estilo_tema(), unsafe_allow_html=True)

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

def guardar_respuestas_supabase(nombre, cedula, respuestas_dict, preguntas_df, puntaje_total, calificacion_final, tiempo_total):
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
                es_correcta = True
            
            registro = {
                'nombre': str(nombre),
                'cedula': str(cedula),
                'pregunta_id': pregunta_id_original,
                'pregunta': str(pregunta),
                'opcion_seleccionada': str(respuesta_seleccionada),
                'opcion_correcta': respuesta_correcta,
                'es_correcta': bool(es_correcta),
                'Calificacion': int(puntaje_total),
                'tiempo_total': int(tiempo_total),
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
        try:
            fila_pregunta = preguntas_df[preguntas_df['PREGUNTAS'] == pregunta].iloc[0]
            if 'RESPUESTA' in fila_pregunta and pd.notna(fila_pregunta['RESPUESTA']):
                respuesta_correcta = fila_pregunta['RESPUESTA']
                if respuesta_seleccionada == respuesta_correcta:
                    puntaje += 1
            else:
                puntaje += 1
        except (IndexError, KeyError):
            continue
    
    calificacion = (puntaje / total_preguntas)
    return puntaje, round(calificacion, 2)

def validar_cedula_numerica(cedula):
    """Validar que la cédula contenga solo números"""
    return cedula.isdigit() and len(cedula) >= 6

# ========= FUNCIONES PARA EL TEMPORIZADOR OPTIMIZADO =========
def inicializar_temporizador():
    """Inicializa el temporizador para la evaluación"""
    if 'tiempo_inicio_evaluacion' not in st.session_state:
        st.session_state.tiempo_inicio_evaluacion = time.time()
    if 'pregunta_actual' not in st.session_state:
        st.session_state.pregunta_actual = 0
    if 'tiempo_inicio_pregunta' not in st.session_state:
        st.session_state.tiempo_inicio_pregunta = time.time()
    if 'tiempos_preguntas' not in st.session_state:
        st.session_state.tiempos_preguntas = {}
    if 'tiempo_inicio_total' not in st.session_state:
        st.session_state.tiempo_inicio_total = time.time()
    if 'auto_refresh_active' not in st.session_state:
        st.session_state.auto_refresh_active = True

def tiempo_restante_pregunta():
    """Calcula el tiempo restante para la pregunta actual (30 segundos)"""
    tiempo_transcurrido = time.time() - st.session_state.tiempo_inicio_pregunta
    tiempo_restante = max(0, 30 - tiempo_transcurrido)
    return tiempo_restante

def avanzar_pregunta():
    """Avanza a la siguiente pregunta y reinicia el temporizador"""
    st.session_state.pregunta_actual += 1
    st.session_state.tiempo_inicio_pregunta = time.time()

def formatear_tiempo(segundos):
    """Formatea los segundos en MM:SS"""
    minutos = int(segundos // 60)
    segundos = int(segundos % 60)
    return f"{minutos:02d}:{segundos:02d}"

def calcular_tiempo_total_evaluacion():
    """Calcula el tiempo total transcurrido desde el inicio de la evaluación"""
    if 'tiempo_inicio_total' in st.session_state:
        tiempo_total = time.time() - st.session_state.tiempo_inicio_total
        return int(tiempo_total)  # Retorna en segundos como entero
    return 0

def crear_display_temporizador_optimizado(tiempo_restante):
    """Crea un display de temporizador optimizado"""
    # Determinar estado del temporizador
    if tiempo_restante > 15:
        estado = "success"
        color = "🟢"
        clase_extra = ""
    elif tiempo_restante > 5:
        estado = "warning"
        color = "🟡"
        clase_extra = "timer-card-warning"
    else:
        estado = "danger"
        color = "🔴"
        clase_extra = "timer-card-danger"
    
    # Calcular porcentaje para barra de progreso
    porcentaje = (tiempo_restante / 30) * 100
    
    return f"""
    <div class="card-adaptive timer-card {clase_extra}">
        <h3 style="margin: 0;">{color} Tiempo restante</h3>
        <h2 style="margin: 5px 0; color: #1f77b4;">{formatear_tiempo(tiempo_restante)}</h2>
        <div style="width: 100%; background-color: #e0e0e0; border-radius: 10px; height: 10px; margin: 10px 0;">
            <div style="width: {porcentaje}%; background-color: {'#4CAF50' if estado == 'success' else '#FFC107' if estado == 'warning' else '#f44336'}; height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """

# ========= INICIALIZAR ESTADO DE LA SESIÓN =========
if 'preguntas_seleccionadas' not in st.session_state:
    st.session_state.preguntas_seleccionadas = pd.DataFrame()
    st.session_state.preguntas_cargadas = False

if 'respuestas_enviadas' not in st.session_state:
    st.session_state.respuestas_enviadas = False

if 'puntaje_final' not in st.session_state:
    st.session_state.puntaje_final = 0

if 'calificacion_final' not in st.session_state:
    st.session_state.calificacion_final = 0.0

if 'evaluacion_iniciada' not in st.session_state:
    st.session_state.evaluacion_iniciada = False

if 'info_personal_validada' not in st.session_state:
    st.session_state.info_personal_validada = False

if 'tiempo_total_evaluacion' not in st.session_state:
    st.session_state.tiempo_total_evaluacion = 0

# ========= INTERFAZ PRINCIPAL =========
# Logo con estilos adaptativos
st.markdown("""
<div style="display: flex; justify-content: center; margin: 10px 0;">
    <div class="logo-container">
        <img src="https://p1-ofp.static.pub/fes/cms/2025/06/16/w6mug9uerf66dejn1o22wi56qonflp942007.svg" 
             width="300">
    </div>
</div>
""", unsafe_allow_html=True)

st.title("📝 Formulario de Evaluación")
st.markdown("---")

# Cargar preguntas si no se han cargado
if not st.session_state.preguntas_cargadas:
    with st.spinner("Cargando preguntas..."):
        df_preguntas = cargar_preguntas()
        if not df_preguntas.empty:
            semilla = random.randint(1, 1000000000)
            st.session_state.preguntas_seleccionadas = df_preguntas.sample(
                n=min(15, len(df_preguntas)), 
                random_state=semilla
            ).reset_index(drop=True)
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
        
        # ========= SECCIÓN DE INFORMACIÓN PERSONAL =========
        if not st.session_state.info_personal_validada:
            st.markdown("## 👤 Información Personal")
            
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                nombre = st.text_input(r"$\textsf{\Large 📝 Nombre completo*}$", key="nombre_usuario")
            
            with col_info2:
                # Campo de cédula con validación numérica
                cedula_input = st.text_input(
                    r"$\textsf{\Large🆔 Número de cédula*}$", 
                    key="cedula_usuario",
                    help="Solo se permiten números",
                    max_chars=15
                )
                
                # Filtrar solo números mientras el usuario escribe
                if cedula_input and not cedula_input.isdigit():
                    st.session_state.cedula_usuario = ''.join(filter(str.isdigit, cedula_input))
                    st.rerun()
            
            # Validación en tiempo real de la cédula
            cedula_valida = False
            if cedula_input:
                if not validar_cedula_numerica(cedula_input):
                    st.error("❌ La cédula debe contener solo números y tener al menos 6 dígitos")
                else:
                    cedula_valida = True
                    st.success("✅ Cédula válida")
            
            # Validar información personal completa
            info_personal_completa = bool(nombre.strip() and cedula_input.strip() and cedula_valida)
            
            if info_personal_completa:
                if st.button("🚀 Comenzar Evaluación", type="primary"):
                    st.session_state.info_personal_validada = True
                    st.session_state.evaluacion_iniciada = True
                    st.session_state.nombre_final = nombre.strip()
                    st.session_state.cedula_final = cedula_input.strip()
                    inicializar_temporizador()
                    st.rerun()
            else:
                st.warning("⚠️ Por favor, completa tu información personal correctamente antes de continuar.")
        
        # ========= SECCIÓN DE EVALUACIÓN CON TEMPORIZADOR OPTIMIZADO =========
        else:
            # Mostrar información del usuario con tarjeta adaptativa
            st.markdown(f"""
            <div class="card-adaptive info-success">
                <strong>👤 {st.session_state.nombre_final} | 🆔 {st.session_state.cedula_final}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Inicializar respuestas si no existen
            if 'respuestas_evaluacion' not in st.session_state:
                st.session_state.respuestas_evaluacion = {}
            
            # Verificar si todas las preguntas están respondidas
            total_preguntas = len(st.session_state.preguntas_seleccionadas)
            preguntas_respondidas = len(st.session_state.respuestas_evaluacion)
            
            if st.session_state.pregunta_actual < total_preguntas:
                # ========= MOSTRAR PREGUNTA ACTUAL CON TEMPORIZADOR =========
                pregunta_idx = st.session_state.pregunta_actual
                row = st.session_state.preguntas_seleccionadas.iloc[pregunta_idx]
                
                pregunta = row["PREGUNTAS"]
                opciones = row["OPCIONES"]
                pregunta_id = row["ID"]
                
                # Calcular tiempo restante
                tiempo_restante = tiempo_restante_pregunta()
                
                # Mostrar temporizador y progreso
                col_timer, col_progress = st.columns([1, 3])
                
                with col_timer:
                    # Display optimizado del temporizador
                    st.markdown(crear_display_temporizador_optimizado(tiempo_restante), unsafe_allow_html=True)
                
                with col_progress:
                    # Mostrar progreso general
                    progreso_general = (pregunta_idx + 1) / total_preguntas
                    st.progress(progreso_general, text=f"Pregunta {pregunta_idx + 1} de {total_preguntas}")
                    
                    # Mostrar estadísticas adicionales
                    col_stats1, col_stats2 = st.columns(2)
                    with col_stats1:
                        st.metric("Respondidas", len(st.session_state.respuestas_evaluacion))
                    with col_stats2:
                        tiempo_total_transcurrido = calcular_tiempo_total_evaluacion()
                        st.metric("Tiempo total", formatear_tiempo(tiempo_total_transcurrido))
                
                st.markdown("---")
                
                # Mostrar la pregunta con tarjeta adaptativa
                st.markdown(f"### Pregunta {pregunta_idx + 1} (ID: {pregunta_id})")
                
                st.markdown(f"""
                <div class="question-card card-adaptive">
                    {pregunta}
                </div>
                """, unsafe_allow_html=True)
                
                # Opciones de respuesta
                respuesta_key = f"respuesta_{pregunta_idx}"
                respuesta = st.radio(
                    "Selecciona tu respuesta:",
                    opciones,
                    key=respuesta_key,
                    index=None
                )
                
                # Botones de control
                col_siguiente, col_saltar = st.columns([2, 1])
                
                with col_siguiente:
                    if respuesta is not None:
                        if st.button("➡️ Siguiente Pregunta", type="primary"):
                            # Guardar respuesta
                            st.session_state.respuestas_evaluacion[pregunta] = respuesta
                            
                            # Avanzar pregunta
                            avanzar_pregunta()
                            st.rerun()
                
                with col_saltar:
                    if st.button("⏭️ Saltar Pregunta"):
                        # Guardar como "Sin respuesta"
                        st.session_state.respuestas_evaluacion[pregunta] = "Sin respuesta"
                        
                        # Avanzar pregunta
                        avanzar_pregunta()
                        st.rerun()
                
                # Auto-avance cuando se acaba el tiempo
                if tiempo_restante <= 0:
                    st.markdown("""
                    <div class="card-adaptive info-error">
                        <strong>⏰ ¡Tiempo agotado! Avanzando automáticamente...</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Si no hay respuesta seleccionada, guardar como "Sin respuesta"
                    if respuesta is None:
                        st.session_state.respuestas_evaluacion[pregunta] = "Sin respuesta"
                    else:
                        st.session_state.respuestas_evaluacion[pregunta] = respuesta
                    
                    # Auto-avanzar con delay
                    time.sleep(2)  # Pausa de 2 segundos para mostrar el mensaje
                    avanzar_pregunta()
                    st.rerun()
                
                # Auto-refresh cada 1 segundo para actualizar el temporizador
                if st.session_state.get('auto_refresh_active', True):
                    # Mostrar indicador de auto-refresh
                    st.markdown(f"""
                    <div class="auto-refresh">
                        ⏱️ Actualizando... {formatear_tiempo(tiempo_restante)}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Usar un placeholder para actualización más suave
                    placeholder = st.empty()
                    with placeholder:
                        time.sleep(1)  # Esperar 1 segundo
                        if tiempo_restante > 1:  # Solo hacer rerun si queda tiempo
                            st.rerun()
            
            else:
                # ========= EVALUACIÓN COMPLETADA =========
                st.markdown("""
                <div class="card-adaptive info-success">
                    <h3 style="margin: 0;">✅ ¡Has completado todas las preguntas!</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar resumen
                st.markdown("## 📋 Resumen de Respuestas")
                respondidas = len([r for r in st.session_state.respuestas_evaluacion.values() if r != "Sin respuesta"])
                sin_responder = len([r for r in st.session_state.respuestas_evaluacion.values() if r == "Sin respuesta"])
                
                col_res1, col_res2, col_res3 = st.columns(3)
                
                with col_res1:
                    st.metric("✅ Respondidas", respondidas)
                
                with col_res2:
                    st.metric("❌ Sin Responder", sin_responder)
                
                with col_res3:
                    st.metric("📊 Total", total_preguntas)
                
                # Mostrar detalle de respuestas
                # with st.expander("📝 Ver detalle de respuestas"):
                #     for i, (pregunta, respuesta) in enumerate(st.session_state.respuestas_evaluacion.items(), 1):
                #         estado = "✅" if respuesta != "Sin respuesta" else "❌"
                #         st.write(f"{estado} **Pregunta {i}:** {respuesta}")
                
                # Botón para finalizar evaluación
                if st.button("💾 Finalizar y Guardar Evaluación", type="primary"):
                    # Detener auto-refresh
                    st.session_state.auto_refresh_active = False
                    
                    with st.spinner("Guardando evaluación..."):
                        # Calcular puntaje y calificación
                        puntaje, calificacion = calcular_puntaje_y_calificacion(
                            st.session_state.respuestas_evaluacion, 
                            st.session_state.preguntas_seleccionadas
                        )
                        st.session_state.puntaje_final = puntaje
                        st.session_state.calificacion_final = calificacion
                        
                        # Calcular tiempo total de la evaluación
                        tiempo_total = calcular_tiempo_total_evaluacion()
                        st.session_state.tiempo_total_evaluacion = tiempo_total
                        
                        # Guardar en Supabase
                        guardado_exitoso = guardar_respuestas_supabase(
                            st.session_state.nombre_final,
                            st.session_state.cedula_final,
                            st.session_state.respuestas_evaluacion,
                            st.session_state.preguntas_seleccionadas,
                            puntaje,
                            calificacion,
                            tiempo_total
                        )
                        
                        if guardado_exitoso:
                            st.success("✅ ¡Evaluación guardada correctamente!")
                            st.session_state.respuestas_enviadas = True
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar la evaluación. Inténtalo de nuevo.")
    
    else:
        # ========= PANTALLA DE RESULTADOS =========
        # Detener auto-refresh
        st.session_state.auto_refresh_active = False
        
        st.success("✅ **¡Formulario completado exitosamente!**")
        st.balloons()

        # Mostrar puntaje con tarjeta adaptativa
        st.markdown("## 🏆 Resultados de la Evaluación")

        st.markdown(f"""
        <div class="gradient-card">
            <h3>Puntaje Final</h3>
            <h1 style="font-size: 2.5em;">{st.session_state.puntaje_final}/15</h1>
            <p style="font-size: 1.1em;">
                {(st.session_state.puntaje_final/15)*100:.0f}% correctas
            </p>
            <p style="font-size: 0.9em;">
                Tiempo total: {formatear_tiempo(st.session_state.tiempo_total_evaluacion)}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # # Mostrar análisis detallado
        # st.markdown("## 📊 Análisis Detallado")
        
        # col_analisis1, col_analisis2, col_analisis3 = st.columns(3)
        
        # with col_analisis1:
        #     st.metric(
        #         "Preguntas Correctas", 
        #         st.session_state.puntaje_final,
        #         delta=f"{st.session_state.puntaje_final - 7.5:.1f}" if st.session_state.puntaje_final >= 7.5 else f"{st.session_state.puntaje_final - 7.5:.1f}"
        #     )
        
        # with col_analisis2:
        #     porcentaje = (st.session_state.puntaje_final/15)*100
        #     st.metric(
        #         "Porcentaje de Aciertos", 
        #         f"{porcentaje:.0f}%",
        #         delta=f"{porcentaje - 50:.0f}%" if porcentaje >= 50 else f"{porcentaje - 50:.0f}%"
        #     )
        
        # with col_analisis3:
        #     tiempo_promedio = st.session_state.tiempo_total_evaluacion / 15
        #     st.metric(
        #         "Tiempo Promedio/Pregunta", 
        #         f"{tiempo_promedio:.1f}s",
        #         delta=f"{30 - tiempo_promedio:.1f}s restante"
        #     )

        # # Clasificación de rendimiento
        # if porcentaje >= 80:
        #     rendimiento = "🏆 Excelente"
        #     color_rendimiento = "#4CAF50"
        # elif porcentaje >= 70:
        #     rendimiento = "👍 Bueno"
        #     color_rendimiento = "#8BC34A"
        # elif porcentaje >= 60:
        #     rendimiento = "📈 Regular"
        #     color_rendimiento = "#FFC107"
        # else:
        #     rendimiento = "📚 Necesita Mejorar"
        #     color_rendimiento = "#FF9800"
        
        # st.markdown(f"""
        # <div class="card-adaptive" style="border-left: 5px solid {color_rendimiento}; text-align: center;">
        #     <h3>Clasificación de Rendimiento</h3>
        #     <h2 style="color: {color_rendimiento}; margin: 10px 0;">{rendimiento}</h2>
        # </div>
        # """, unsafe_allow_html=True)

        # st.markdown("""
        # ### ¡Gracias por completar la evaluación!
        # ✅ Tus respuestas han sido guardadas en la base de datos  
        # ✅ Tu puntaje ha sido registrado  
        # ✅ Los datos están disponibles para análisis  
        # """)

        # # Opción para reiniciar la evaluación
        # if st.button("🔄 Realizar Nueva Evaluación"):
        #     # Limpiar todo el estado
        #     keys_to_clear = [
        #         'preguntas_seleccionadas', 'preguntas_cargadas', 'respuestas_enviadas',
        #         'puntaje_final', 'calificacion_final', 'evaluacion_iniciada',
        #         'info_personal_validada', 'tiempo_total_evaluacion', 'respuestas_evaluacion',
        #         'pregunta_actual', 'tiempo_inicio_pregunta', 'tiempo_inicio_total',
        #         'auto_refresh_active', 'nombre_final', 'cedula_final'
        #     ]
        #     for key in keys_to_clear:
        #         if key in st.session_state:
        #             del st.session_state[key]
        #     st.rerun()

# ========= SIDEBAR CON INFORMACIÓN =========
with st.sidebar:
    st.header("ℹ️ Información")
    st.markdown("""
    **Instrucciones:**
    1. ✅ Completa tu información personal
    2. 🚀 Haz clic en 'Comenzar Evaluación'
    3. ⏱️ Responde cada pregunta en máximo 30 segundos
    4. 🔄 El sistema se actualiza automáticamente
    5. ⏭️ Avanza automáticamente si se agota el tiempo
    6. 💾 Al finalizar, se guardará tu evaluación
    
    **Sistema de Puntuación:**
    - ✅ Cada pregunta correcta = 1 punto
    - 🎯 Puntaje máximo = 15 puntos
    - ⏰ Tiempo límite: 30 segundos por pregunta
    - 📊 Clasificación automática de rendimiento
    """)
    
    # Mostrar estadísticas de la sesión
    if st.session_state.respuestas_enviadas:
        st.markdown("---")
        st.markdown("### 📊 Estadísticas Finales")
        st.metric("Puntaje Final", f"{st.session_state.puntaje_final}/15")
        st.metric("Porcentaje", f"{(st.session_state.puntaje_final/15)*100:.0f}%")
        st.metric("Tiempo Total", f"{formatear_tiempo(st.session_state.tiempo_total_evaluacion)}")
        
        # # Mostrar clasificación en sidebar también
        # porcentaje = (st.session_state.puntaje_final/15)*100
        # if porcentaje >= 80:
        #     st.success("🏆 Rendimiento: Excelente")
        # elif porcentaje >= 70:
        #     st.success("👍 Rendimiento: Bueno")
        # elif porcentaje >= 60:
        #     st.warning("📈 Rendimiento: Regular")
        # else:
        #     st.info("📚 Rendimiento: Necesita Mejorar")
    
    # Mostrar información de la evaluación activa
    elif st.session_state.get('evaluacion_iniciada', False) and not st.session_state.respuestas_enviadas:
        st.markdown("---")
        st.markdown("### 📈 Progreso Actual")
        if st.session_state.pregunta_actual < len(st.session_state.preguntas_seleccionadas):
            respondidas = len(st.session_state.get('respuestas_evaluacion', {}))
            st.metric("Preguntas completadas", f"{respondidas}/15")
            
            # Calcular tiempo transcurrido total
            if 'tiempo_inicio_total' in st.session_state:
                tiempo_transcurrido = time.time() - st.session_state.tiempo_inicio_total
                st.metric("Tiempo transcurrido", formatear_tiempo(tiempo_transcurrido))
            
            # Mostrar pregunta actual
            st.metric("Pregunta actual", f"{st.session_state.pregunta_actual + 1}")
            
            # Mostrar tiempo restante de la pregunta actual
            tiempo_restante = tiempo_restante_pregunta()
            if tiempo_restante > 15:
                st.success(f"⏰ Tiempo: {formatear_tiempo(tiempo_restante)}")
            elif tiempo_restante > 5:
                st.warning(f"⏰ Tiempo: {formatear_tiempo(tiempo_restante)}")
            else:
                st.error(f"⏰ Tiempo: {formatear_tiempo(tiempo_restante)}")
    
    # Estado de auto-refresh
    if st.session_state.get('auto_refresh_active', False):
        st.markdown("---")
        st.markdown("### 🔄 Sistema")
        st.success("✅ Auto-actualización activa")
        if st.button("⏸️ Pausar Auto-refresh"):
            st.session_state.auto_refresh_active = False
            st.rerun()
    elif st.session_state.get('evaluacion_iniciada', False):
        st.markdown("---")
        st.markdown("### 🔄 Sistema")
        st.warning("⏸️ Auto-actualización pausada")
        if st.button("▶️ Reanudar Auto-refresh"):
            st.session_state.auto_refresh_active = True
            st.rerun()

# # ========= FOOTER CON INFORMACIÓN TÉCNICA =========
# st.markdown("---")
# st.markdown("""
# <div style="text-align: center; color: #666; font-size: 12px; margin: 20px 0;">
#     <p>🔧 <strong>Temporizador Optimizado</strong> - Compatible con todos los dispositivos</p>
#     <p>⚡ Actualización automática cada segundo | 📱 Optimizado para móviles | 💾 Guardado automático</p>
# </div>
# """, unsafe_allow_html=True)