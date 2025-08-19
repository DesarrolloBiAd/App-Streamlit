import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configuración de correo (configura estas variables)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # Para Gmail
    'smtp_port': 587,
    'email_usuario': 'notificaciones.bi.adecco@gmail.com',  # Tu email
    'email_password': 'bgiu ydmq derj ikns',  # Contraseña de aplicación
    'email_destinatario': 'Dairon.Alonso@adecco.com'  # Email donde enviar las respuestas
}

# Cargar banco de preguntas con encabezado manual
@st.cache_data
def cargar_preguntas():
    # Usar ruta relativa al archivo actual
    ruta_archivo = os.path.join(os.path.dirname(__file__), "Preguntas.csv")
    
    # Si no existe, buscar en el directorio actual
    if not os.path.exists(ruta_archivo):
        ruta_archivo = "Preguntas.csv"
    
    try:
        df = pd.read_csv(
            ruta_archivo,
            sep=';', header=None, names=['ID', 'Pregunta', 'Opciones'], encoding='latin1'
        )
        # Convertir la columna de opciones en listas
        df['Opciones'] = df['Opciones'].apply(lambda x: [op.strip() for op in str(x).split(';')])
        return df
    except FileNotFoundError:
        st.error("No se encontró el archivo Preguntas.csv")
        return pd.DataFrame()

def enviar_email(respuestas_dict):
    """Función para enviar las respuestas por correo electrónico"""
    try:
        # Crear el mensaje
        mensaje = MIMEMultipart()
        mensaje['From'] = EMAIL_CONFIG['email_usuario']
        mensaje['To'] = EMAIL_CONFIG['email_destinatario']
        mensaje['Subject'] = f"Respuestas del Formulario - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Crear el cuerpo del email
        cuerpo = "RESPUESTAS DEL FORMULARIO DE EVALUACIÓN\n"
        cuerpo += "=" * 50 + "\n\n"
        cuerpo += f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for i, (pregunta, respuesta) in enumerate(respuestas_dict.items(), 1):
            cuerpo += f"{i}. {pregunta}\n"
            cuerpo += f"   Respuesta: {respuesta}\n\n"
        
        mensaje.attach(MIMEText(cuerpo, 'plain'))
        
        # Conectar al servidor SMTP y enviar
        servidor = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        servidor.starttls()
        servidor.login(EMAIL_CONFIG['email_usuario'], EMAIL_CONFIG['email_password'])
        
        texto = mensaje.as_string()
        servidor.sendmail(EMAIL_CONFIG['email_usuario'], EMAIL_CONFIG['email_destinatario'], texto)
        servidor.quit()
        
        return True
    except Exception as e:
        st.error(f"Error al enviar el correo: {str(e)}")
        return False

def guardar_respuestas_csv(respuestas_dict):
    """Función para guardar las respuestas en CSV"""
    try:
        # Agregar timestamp a las respuestas
        respuestas_con_fecha = {
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            **respuestas_dict
        }
        
        df_respuestas = pd.DataFrame([respuestas_con_fecha])
        
        # Verificar si el archivo existe para decidir si incluir header
        archivo_existe = os.path.exists("respuestas.csv")
        
        df_respuestas.to_csv(
            "respuestas.csv", 
            mode='a', 
            index=False, 
            header=not archivo_existe,
            encoding='utf-8',
            sep=';'
        )
        return True
    except Exception as e:
        st.error(f"Error al guardar en CSV: {str(e)}")
        return False

# Inicializar el estado de la sesión
if 'preguntas_seleccionadas' not in st.session_state:
    df_preguntas = cargar_preguntas()
    if not df_preguntas.empty:
        st.session_state.preguntas_seleccionadas = df_preguntas.sample(n=min(10, len(df_preguntas))).reset_index(drop=True)
    else:
        st.session_state.preguntas_seleccionadas = pd.DataFrame()

if 'respuestas_enviadas' not in st.session_state:
    st.session_state.respuestas_enviadas = False

# Interfaz principal
st.title("📝 Formulario de Evaluación")
st.markdown("---")

# Verificar si hay preguntas cargadas
if st.session_state.preguntas_seleccionadas.empty:
    st.error("No se pudieron cargar las preguntas. Verifica que el archivo 'Preguntas.csv' existe.")
else:
    # Mostrar información de la sesión
    st.info(f"📊 Preguntas seleccionadas para esta sesión: {len(st.session_state.preguntas_seleccionadas)}")
    
    if not st.session_state.respuestas_enviadas:
        respuestas = {}
        
        # Mostrar preguntas con sus opciones específicas
        for idx, row in st.session_state.preguntas_seleccionadas.iterrows():
            pregunta = row["Pregunta"]
            opciones = row["Opciones"]
            
            st.markdown(f"### Pregunta {idx + 1}")
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
        
        # Mostrar progreso
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
            enviar_habilitado = preguntas_respondidas == total_preguntas
            if st.button("📧 Enviar Respuestas", disabled=not enviar_habilitado):
                if enviar_habilitado:
                    # Guardar en CSV
                    csv_guardado = guardar_respuestas_csv(respuestas)
                    
                    # Enviar por correo
                    email_enviado = enviar_email(respuestas)
                    
                    if csv_guardado and email_enviado:
                        st.success("✅ ¡Respuestas enviadas correctamente por correo y guardadas en archivo!")
                        st.session_state.respuestas_enviadas = True
                        st.rerun()
                    elif csv_guardado:
                        st.warning("⚠️ Respuestas guardadas en archivo, pero no se pudo enviar el correo.")
                        st.session_state.respuestas_enviadas = True
                        st.rerun()
                    else:
                        st.error("❌ Error al procesar las respuestas. Inténtalo de nuevo.")
                else:
                    st.error("Por favor, responde todas las preguntas antes de enviar.")
        
        if not enviar_habilitado and preguntas_respondidas > 0:
            st.warning(f"⚠️ Faltan {total_preguntas - preguntas_respondidas} pregunta(s) por responder.")
    
    else:
        # Pantalla de confirmación
        st.success("✅ **¡Formulario completado exitosamente!**")
        st.balloons()
        
        st.markdown("""
        ### ¡Gracias por completar la evaluación!
        
        ✅ Tus respuestas han sido guardadas  
        ✅ Se ha enviado una copia por correo electrónico  
        ✅ Los datos están disponibles para análisis  
        """)
        
        if st.button("🔄 Realizar Otra Evaluación"):
            # Reiniciar la sesión
            df_preguntas = cargar_preguntas()
            if not df_preguntas.empty:
                st.session_state.preguntas_seleccionadas = df_preguntas.sample(n=min(10, len(df_preguntas))).reset_index(drop=True)
            st.session_state.respuestas_enviadas = False
            st.rerun()

# Sidebar con información
with st.sidebar:
    st.header("ℹ️ Información")
    st.markdown("""
    **Instrucciones:**
    1. Responde todas las preguntas
    2. Haz clic en 'Enviar Respuestas'
    3. Las respuestas se guardarán y enviarán por correo
    
    **Configuración necesaria:**
    - Archivo 'Preguntas.csv' en el directorio
    - Configurar credenciales de email en el código
    """)
    
    if st.button("📊 Ver Estadísticas"):
        if os.path.exists("respuestas.csv"):
            df_stats = pd.read_csv("respuestas.csv", sep=';')
            st.write(f"Total de respuestas: {len(df_stats)}")
            st.write("Últimas 5 evaluaciones:")
            st.dataframe(df_stats.tail().iloc[:, :3])  # Mostrar solo primeras 3 columnas