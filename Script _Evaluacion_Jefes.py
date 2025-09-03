import streamlit as st
import pandas as pd
import os
import base64
import datetime
import time
from supabase import create_client, Client

# Configuración de la página
st.set_page_config(
    page_title="Evaluación Promotores",
    page_icon="https://p3-ofp.static.pub//fes/cms/2025/01/16/7aiyjr6t3hszpzvsfnbwip54i0ovkz395647.png",
    layout="wide"
)

# 🎨 Estilos personalizados
st.markdown("""
    <style>
        .stApp {
            background-color: #1a2b3c;
            color: #ffffff;
        }
        h1, h2, h3, h4, h5, h6, p, label, .markdown-text-container, .stMarkdown, .stTextInput, .stSelectbox, .stRadio, .stExpander, .stSubheader {
            color: #ffffff !important;
        }
        .stButton button {
            background-color: #3498db;
            color: white;
            font-weight: bold;
            border-radius: 6px;
            padding: 8px 16px;
        }
        .stButton button:hover {
            background-color: #2980b9;
        }
        .streamlit-expanderHeader {
            color: #ffffff;
            font-weight: bold;
        }
        footer {
            visibility: hidden;
        }
        textarea {
            background-color: #2c3e50;
            color: #ffffff;
        }
        .logo-box {
            background-color: white;
            border-radius: 12px;
            padding: 10px;
            height: 150px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .logo-box img {
            max-height: 100px;
        }
        img {
            border-radius: 0 !important;
        }
    </style>
""", unsafe_allow_html=True)

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

# Función para cargar imagen
def load_image(image_path):
    try:
        return image_path
    except:
        return None

# Inicializar session state para controlar el reset del formulario
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Contador de sesión para reset completo del formulario
if 'session_counter' not in st.session_state:
    st.session_state.session_counter = 0

# Logos iniciales: Motorola y Adecco más grandes y alineados en extremos
col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    try:
        st.image("https://441041d6dc.imgdist.com/pub/bfra/989mykjl/ioe/8x8/qt0/Motorla%20540-170.png", width=300)
    except:
        st.write("Logo Motorola")

with col3:
    try:
        st.image("https://441041d6dc.imgdist.com/pub/bfra/989mykjl/3jw/n2n/7ki/Logo%20Adecco.png", width=300)
    except:
        st.write("Logo Adecco")

# Título centrado debajo de los logos
st.markdown("<h1 style='text-align: center; color: white;'>Formulario de Evaluación Promotores</h1>", unsafe_allow_html=True)

st.subheader("Evaluación de Desempeño por Jefe Directo")

# Datos de jefes con región y cargo
jefes_data = [
    {"NOMBRE": "Angel Alberto Charry Garrido", "CARGO": "Ejecutivo de Cuenta", "Regional": "Centro"},
    {"NOMBRE": "Anuar Javier Contreras Olivera", "CARGO": "Ejecutivo de Cuenta", "Regional": "Norte"},
    {"NOMBRE": "Jeimy Carolina Salamanca Porras", "CARGO": "Ejecutivo de Cuenta", "Regional": "Centro"},
    {"NOMBRE": "Jorge Eliecer Orozco Bocanegra", "CARGO": "Ejecutivo de Cuenta", "Regional": "Centro"},
    {"NOMBRE": "Oscardy Molina Espinosa", "CARGO": "Ejecutivo de Cuenta", "Regional": "Suroccidente"},
    {"NOMBRE": "Roosvelt Alexander Sanchez Caro", "CARGO": "Ejecutivo de Cuenta", "Regional": "Noroccidente"},  
    {"NOMBRE": "Silvia Isabel Rojas Sanchez", "CARGO": "Ejecutivo de Cuenta", "Regional": "Norte"},
    {"NOMBRE": "Julian Camilo Diaz Ruiz", "CARGO": "Ejecutivo de Cuenta JR", "Regional": "Centro"},
    {"NOMBRE": "Oscar Dario Redondo Suarez", "CARGO": "Ejecutivo de Cuenta JR", "Regional": "Norte"},
    {"NOMBRE": "Sergio Arturo Roldan", "CARGO": "Jefe De Zona", "Regional": "Suroccidente"},
    {"NOMBRE": "Kevin Andres Torres Jimenez", "CARGO": "Jefe De Zona", "Regional": "Norte"},
    {"NOMBRE": "Samuel Ruiz Pinzon", "CARGO": "Jefe De Zona", "Regional": "Suroccidente"},
    {"NOMBRE": "Andres Orlando Cubides Franco", "CARGO": "Jefe De Zona", "Regional": "Centro"},
    {"NOMBRE": "Beatriz Elena Morales Martinez", "CARGO": "Jefe De Zona", "Regional": "Noroccidente"},
    {"NOMBRE": "Diana Carolina Marin Chaverra", "CARGO": "Jefe De Zona", "Regional": "Noroccidente"},
    {"NOMBRE": "Didier Gonzalez Aristizabal", "CARGO": "Jefe De Zona", "Regional": "Noroccidente"},
    {"NOMBRE": "Gineth Mantilla Henao", "CARGO": "Jefe De Zona", "Regional": "Suroccidente"},
    {"NOMBRE": "Gustavo Adolfo Calvo Restrepo", "CARGO": "Jefe De Zona", "Regional": "Noroccidente"},
    {"NOMBRE": "Ivan Camilo Avila Salcedo", "CARGO": "Jefe De Zona", "Regional": "Centro"},
    {"NOMBRE": "Jesus Leandro Valero Diaz", "CARGO": "Jefe De Zona", "Regional": "Norte"},
    {"NOMBRE": "Joceline Yesenia Maya Cueltan", "CARGO": "Jefe De Zona", "Regional": "Suroccidente"},
    {"NOMBRE": "Julie Hasbleidy Gonzalez Romero", "CARGO": "Jefe De Zona", "Regional": "Centro"},
    {"NOMBRE": "Javier Jimenez", "CARGO": "Jefe De Zona", "Regional": "Centro"},
    {"NOMBRE": "Lina Maria Gonzalez Grisales", "CARGO": "Jefe De Zona", "Regional": "Centro"},
    {"NOMBRE": "Julian Medina", "CARGO": "Jefe De Zona", "Regional": "Centro"},
    {"NOMBRE": "Tulio Cesar Muriel Duran", "CARGO": "Jefe De Zona", "Regional": "Noroccidente"},
    {"NOMBRE": "Yessica Andrea Fonseca Lara", "CARGO": "Jefe De Zona", "Regional": "Centro"},
    {"NOMBRE": "Yudi Milena Pineros Garcia", "CARGO": "Jefe De Zona", "Regional": "Centro"},
    {"NOMBRE": "Luis Angel Ramirez Garces", "CARGO": "Jefe De Zona", "Regional": "Centro"},
    {"NOMBRE": "Cristhian Camilo Penagos Montaño", "CARGO": "Jefe De Zona", "Regional": "Suroccidente"},
    {"NOMBRE": "Angie Daniela Prieto Velasquez", "CARGO": "Jefe De Zona", "Regional": "Centro"},
    {"NOMBRE": "Maria Shirey Quintero", "CARGO": "Jefe De Zona", "Regional": "Norte"}
]

df_jefes = pd.DataFrame(jefes_data)

# Selección de región - con índice por defecto en 0 (opción vacía)
regiones = [""] + sorted(df_jefes["Regional"].unique())
region_seleccionada = st.selectbox("Selecciona la Región", regiones, 
                                   index=0,  # Forzar índice 0
                                   key=f"region_{st.session_state.session_counter}")

if region_seleccionada:
    # Filtrar por región
    df_filtrado_region = df_jefes[df_jefes["Regional"] == region_seleccionada]
    
    # Selección de cargo - con índice por defecto en 0 (opción vacía)
    cargos = [""] + sorted(df_filtrado_region["CARGO"].unique())
    cargo_seleccionado = st.selectbox("Selecciona el Cargo", cargos, 
                                      index=0,  # Forzar índice 0
                                      key=f"cargo_{st.session_state.session_counter}")
    
    if cargo_seleccionado:
        # Filtrar por región y cargo
        df_filtrado_final = df_filtrado_region[df_filtrado_region["CARGO"] == cargo_seleccionado]
        
        # Selección de jefe - con índice por defecto en 0 (opción vacía)
        jefes = [""] + sorted(df_filtrado_final["NOMBRE"].unique())
        jefe_seleccionado = st.selectbox("Selecciona el Jefe", jefes, 
                                        index=0,  # Forzar índice 0
                                        key=f"jefe_{st.session_state.session_counter}")
    else:
        jefe_seleccionado = ""
else:
    cargo_seleccionado = ""
    jefe_seleccionado = ""

# Ingreso manual del nombre y cédula del vendedor
st.subheader("Datos del Promotor Evaluado")
nombre_vendedor = st.text_input("Nombre del Promotor", 
                               value="",  # Valor vacío por defecto
                               key=f"nombre_{st.session_state.session_counter}")
cedula_vendedor = st.text_input("Cédula del Promotor", 
                               value="",  # Valor vacío por defecto
                               key=f"cedula_{st.session_state.session_counter}")

# Validación: solo números y longitud entre 6 y 10
cedula_valida = True
if cedula_vendedor and (not cedula_vendedor.isdigit() or not (6 <= len(cedula_vendedor) <= 10)):
    st.warning("La cédula debe contener solo números y tener entre 6 y 10 dígitos.")
    cedula_valida = False

# Solo mostrar preguntas si se han seleccionado región, cargo y jefe
if region_seleccionada and cargo_seleccionado and jefe_seleccionado:
    # Preguntas fijas
    st.subheader("Responde las Siguientes Preguntas:")

    respuestas = {}

    preguntas_opcion_multiple = {
        "1. ¿Cómo transforma las características del producto en beneficios tangibles para el cliente?": ["No Presenta la Competencia", "Por Mejorar", "Bueno", "Sobresaliente", "Excelente"],
        "2. ¿Durante el proceso de venta, realiza demostraciones efectivas del producto? (Experiencia)": ["No Presenta la Competencia", "Por Mejorar", "Bueno", "Sobresaliente", "Excelente"],
        "3. ¿Maneja las objeciones de los clientes y dirige la conversación hacia el cierre de la venta?": ["No Presenta la Competencia", "Por Mejorar", "Bueno", "Sobresaliente", "Excelente"],
        "4. ¿Tiene conocimiento actualizado sobre las ofertas, precios y características de los productos de la competencia?": ["No Presenta la Competencia", "Por Mejorar", "Bueno", "Sobresaliente", "Excelente"],
        "5. ¿Mantiene los productos, el material POP y el área de exhibición en óptimas condiciones, siguiendo los lineamientos de la empresa?": ["No Presenta la Competencia", "Por Mejorar", "Bueno", "Sobresaliente", "Excelente"],
        "6. ¿Maneja cifras y terminos clave del punto de venta (como Market Share, TAM, Proyeccion y Cumplimiento) y las utiliza para tomar decisiones?": ["No Presenta la Competencia", "Por Mejorar", "Bueno", "Sobresaliente", "Excelente"],
        "7. ¿Diligencia correctamente los formularios y planillas de la carpeta comercial?": ["No Presenta la Competencia", "Por Mejorar", "Bueno", "Sobresaliente", "Excelente"],
        "8. ¿Atiende de manera oportuna y respetuosa las solicitudes de clientes internos y externos?":["No Presenta la Competencia", "Por Mejorar", "Bueno", "Sobresaliente", "Excelente"],
        "9. ¿Comunica de forma clara y puntual las novedades y/o solicitudes que surgen en su labor diaria?":["No Presenta la Competencia", "Por Mejorar", "Bueno", "Sobresaliente", "Excelente"],
        "10. ¿Cumple con las encuestas diarias de Mototalk?":["No Presenta la Competencia", "Por Mejorar", "Bueno", "Sobresaliente", "Excelente"],
        "11. ¿Mantiene una actitud proactiva y persuasiva frente al  consumidor? (abordaje efectivo)":["No Presenta la Competencia", "Por Mejorar", "Bueno", "Sobresaliente", "Excelente"],
        "12. ¿Continuaria con el promotor?": ["Sí", "No"],
        "13. El especialista tiende a tener mejor resultados cuando trabaja en":["Equipo", "Individualmente"],
        "14. ¿Identifica si el especialista tiene sentido de pertenencia hacia la marca?":["Sí", "No"],
        "15. ¿Identifica en el especialista actitudes de liderazgo que lo destaquen entre sus compañeros?":["Sí", "No"]
    }

    # Crear claves únicas para cada radio button - con índice forzado en 0
    for i, (pregunta, opciones) in enumerate(preguntas_opcion_multiple.items()):
        # Agregar opción vacía al inicio
        opciones_con_vacio = ["Seleccionar..."] + opciones
        respuesta = st.radio(pregunta, opciones_con_vacio, 
                            index=0,  # Forzar índice 0 (Seleccionar...)
                            key=f"pregunta_{i}_{st.session_state.session_counter}")
        if respuesta != "Seleccionar...":
            respuestas[pregunta] = respuesta
        else:
            respuestas[pregunta] = None

    # Pregunta de campo abierto
    comentario_adicional = st.text_area("¿Tienes algún comentario adicional sobre el vendedor?", 
                                       value="",  # Valor vacío por defecto
                                       key=f"comentario_{st.session_state.session_counter}")
    respuestas["Comentario adicional"] = comentario_adicional

    # Validar que todas las preguntas estén respondidas
    preguntas_sin_responder = [p for p, r in respuestas.items() if r is None and p != "Comentario adicional"]
    
    if st.button("Enviar encuesta", key=f"enviar_{st.session_state.session_counter}"):
        # Validaciones
        if not jefe_seleccionado or not nombre_vendedor or not cedula_vendedor:
            st.error("Por favor, completa todos los campos obligatorios antes de enviar.")
        elif not cedula_valida:
            st.error("Por favor, corrige la cédula antes de enviar.")
        elif preguntas_sin_responder:
            st.error(f"Por favor, responde todas las preguntas antes de enviar. Faltan: {len(preguntas_sin_responder)} preguntas.")
        else:
            supabase = crear_conexion_supabase()
            
            if not supabase:
                st.error("No se pudo establecer conexión con la base de datos.")
            else:
                registros_exitosos = 0
                
                # Fecha y hora actual
                fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Crear una fila por cada pregunta
                filas = []
                for pregunta, respuesta in respuestas.items():
                    if pregunta != "Comentario adicional" and respuesta is not None:
                        fila = {
                            "Cedula del Promotor": str(cedula_vendedor),
                            "Nombre del Promotor": str(nombre_vendedor),
                            "Jefe de zona": str(jefe_seleccionado),
                            "Region": str(region_seleccionada),
                            "Cargo Jefe": str(cargo_seleccionado),
                            "Fecha y hora": fecha_hora,
                            "Pregunta": str(pregunta),
                            "Respuesta": str(respuesta),
                            "Comentario adicional": str(comentario_adicional)
                        }
                        filas.append(fila)
                
                # Insertar cada fila en la base de datos
                for registro in filas:
                    try:
                        response = supabase.table("Evaluacion promotor").insert(registro).execute()
                        if response.data:
                            registros_exitosos += 1
                        else:
                            st.error(f"Error al insertar registro: No se recibieron datos")
                            
                    except Exception as e:
                        st.error(f"Error al guardar registro: {str(e)}")
                        st.write("Registro que causó el error:", registro)
                
                # Mostrar resultado
                if registros_exitosos == len(filas):
                    st.success(f"✅ Encuesta enviada correctamente. Se guardaron {registros_exitosos} respuestas.")
                    # Incrementar contador de sesión para resetear el formulario
                    st.session_state.session_counter += 1
                    time.sleep(2)
                    st.rerun()
                elif registros_exitosos > 0:
                    st.warning(f"⚠️ Se guardaron {registros_exitosos} de {len(filas)} respuestas. Revisa los errores anteriores.")
                else:
                    st.error("❌ No se pudo guardar ninguna respuesta. Intenta nuevamente.")

st.markdown("""
<hr style="border:1px solid #ccc; margin-top:40px;">

<div style='text-align: center; font-size: 12px; color: gray;'>
Desarrollado por <strong>Manuel Esteban Pimentel Alvarez</strong> - Analista BI Adecco BPO Colombia<br>
© 2025 Todos los derechos reservados
</div>
""", unsafe_allow_html=True)
