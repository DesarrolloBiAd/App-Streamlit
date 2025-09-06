import streamlit as st
import pandas as pd
import os
import base64
import datetime
import time
import pytz
from supabase import create_client, Client


# Configuración de la página
st.set_page_config(
    page_title="Evaluación Promotores",
    page_icon="https://p3-ofp.static.pub//fes/cms/2025/01/16/7aiyjr6t3hszpzvsfnbwip54i0ovkz395647.png",
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
        
        /* AUMENTAR TAMAÑO DE LETRA EN SELECTBOX */
        .stSelectbox label p {
            font-size: 18px !important;
            font-weight: bold !important;
        }
        
        /* Tamaño de letra en las opciones del dropdown */
        .stSelectbox div[data-baseweb="select"] > div {
            font-size: 16px !important;
        }
        
        /* Tamaño de letra en el menú desplegable */
        div[role="listbox"] li {
            font-size: 16px !important;
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


# Validación de fecha límite MEJORADA
def verificar_fecha_limite():
    """Verificar si la encuesta aún está disponible"""
    colombia_tz = pytz.timezone('America/Bogota')
    ahora = datetime.datetime.now(colombia_tz)
    fecha_limite = datetime.datetime(2025, 9, 8, 23, 59, 59, tzinfo=colombia_tz)
    
    return ahora <= fecha_limite, fecha_limite, ahora


# CRONÓMETRO FUNCIONAL SIN JAVASCRIPT - VERSIÓN ACTUALIZADA SIN SEGUNDOS
def mostrar_cronometro():
    """Mostrar cronómetro funcional que se actualiza automáticamente cada minuto"""
    encuesta_disponible, fecha_limite, ahora = verificar_fecha_limite()
    
    if not encuesta_disponible:
        st.error("🚨 **ENCUESTA CERRADA - TIEMPO AGOTADO**")
        st.markdown(f"""
        <div style="text-align: center; background-color: #ff4757; color: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3>⏰ La encuesta ha finalizado</h3>
            <p><strong>Fecha límite:</strong> Lunes 8 de Septiembre, 11:59 PM (Hora Colombia)</p>
            <p><strong>Hora actual:</strong> {ahora.strftime('%d/%m/%Y - %H:%M')} (Colombia)</p>
        </div>
        """, unsafe_allow_html=True)
        return False
    else:
        # Calcular tiempo restante con más precisión
        tiempo_restante = fecha_limite - ahora
        
        # Obtener el total de segundos y convertir correctamente
        total_segundos = int(tiempo_restante.total_seconds())
        
        # Agregar 4 minutos (240 segundos) al total de segundos
        total_segundos += 240  # 4 minutos = 240 segundos
        
        # Calcular días, horas y minutos correctamente
        dias = total_segundos // (24 * 3600)
        horas = (total_segundos % (24 * 3600)) // 3600
        minutos = (total_segundos % 3600) // 60
        
        # Determinar urgencia y color
        if dias <= 1:
            color_fondo = "#ff4757"
            emoji = "🚨"
            urgencia = "¡ÚLTIMO DÍA!"
            tipo_alerta = "error"
        elif dias <= 3:
            color_fondo = "#ff9800"
            emoji = "⚠️"
            urgencia = "¡POCOS DÍAS RESTANTES!"
            tipo_alerta = "warning"
        else:
            color_fondo = "#4ecdc4"
            emoji = "⏰"
            urgencia = ""
            tipo_alerta = "info"
        
        # Mostrar alerta según urgencia
        if tipo_alerta == "error":
            st.error(f"{emoji} {urgencia}")
        elif tipo_alerta == "warning":
            st.warning(f"{emoji} {urgencia}")
        else:
            st.info(f"{emoji} {urgencia}")
        
        # Cronómetro usando columnas de Streamlit (SIN SEGUNDOS)
        st.markdown("### TIEMPO RESTANTE PARA COMPLETAR LAS EVALUACIONES")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="text-align: center; background-color: {color_fondo}; color: white; padding: 5px; border-radius: 10px; margin: 5px;">
                <div style="margin: 0; font-size: 36px; font-weight: bold;">{dias}</div>
                <p style="margin: 0; font-weight: bold;">DÍAS</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="text-align: center; background-color: {color_fondo}; color: white; padding: 5px; border-radius: 10px; margin: 5px;">
                <div style="margin: 0; font-size: 36px; font-weight: bold;">{horas}</div>
                <p style="margin: 0; font-weight: bold;">HORAS</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style="text-align: center; background-color: {color_fondo}; color: white; padding: 5px; border-radius: 10px; margin: 5px;">
                <div style="margin: 0; font-size: 36px; font-weight: bold;">{minutos}</div>
                <p style="margin: 0; font-weight: bold;">MINUTOS</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Información adicional
        st.markdown(f"""
        <div style="text-align: center; background-color: rgba(52, 152, 219, 0.1); padding: 15px; border-radius: 8px; margin: 20px 0;">
            <p><strong>📅 Fecha límite:</strong> Lunes 8 de Septiembre, 11:59 PM (Hora Colombia)</p>
            <p><strong>🕒 Hora actual:</strong> {ahora.strftime('%d/%m/%Y - %H:%M')} (Colombia)</p>
        </div>
        """, unsafe_allow_html=True)
        
        return True


# Configuración para auto-actualización del cronómetro
def configurar_auto_actualizacion():
    """Configurar actualización automática cada minuto"""
    # Obtener el minuto actual
    ahora = datetime.datetime.now(pytz.timezone('America/Bogota'))
    minuto_actual = ahora.minute
    
    # Guardar en session_state para control
    if 'ultimo_minuto' not in st.session_state:
        st.session_state.ultimo_minuto = minuto_actual
    
    # Si cambió el minuto, actualizar la página
    if st.session_state.ultimo_minuto != minuto_actual:
        st.session_state.ultimo_minuto = minuto_actual
        # st.rerun()


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
        st.image("https://441041d6dc.imgdist.com/pub/bfra/989mykjl/kgn/kv6/066/Logo%20Moto%20%281%29.png", width=300)
    except:
        st.write("Logo Motorola")


with col3:
    try:
        st.image("https://441041d6dc.imgdist.com/pub/bfra/989mykjl/3jw/n2n/7ki/Logo%20Adecco.png", width=300)
    except:
        st.write("Logo Adecco")


# Llamar a la configuración de auto-actualización ANTES del cronómetro
configurar_auto_actualizacion()

# MOSTRAR CRONÓMETRO Y VERIFICAR DISPONIBILIDAD
encuesta_disponible = mostrar_cronometro()


if not encuesta_disponible:
    # Mostrar mensaje adicional y detener la aplicación
    st.markdown("""
    <div style="text-align: center; padding: 50px 20px; background-color: rgba(255,71,87,0.1); border-radius: 15px; margin: 20px 0;">
        <h2 style="color: #ff4757;">❌ La encuesta ha finalizado</h2>
        <p style="font-size: 16px;">Gracias por tu interés. La fecha límite para completar la evaluación ya pasó.</p>
        <p style="font-size: 14px; color: #7f8c8d;">
            Si tienes alguna consulta, contacta al equipo de Adecco BPO Colombia.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer siempre visible
    st.markdown("""
    <hr style="border:1px solid #ccc; margin-top:40px;">
    <div style='text-align: center; font-size: 12px; color: gray;'>
    Desarrollado por <strong>Manuel Esteban Pimentel Alvarez</strong> - Analista BI Adecco BPO Colombia<br>
    © 2025 Todos los derechos reservados
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()  # Detener toda la ejecución de la aplicación


# CONTINUAR CON EL RESTO DE LA APLICACIÓN SOLO SI LA ENCUESTA ESTÁ DISPONIBLE
else:
    # Título centrado debajo de los logos
    st.markdown("<h1 style='text-align: center; color: white;'>Formulario de Evaluación Promotores</h1>", unsafe_allow_html=True)


    st.subheader("Evaluación de Desempeño por Jefe Directo")


    # Datos de jefes con región y cargo
    jefes_data = [
        {"NOMBRE": "Angel Alberto Charry Garrido", "CARGO": "Ejecutivo de Cuenta", "Regional": "Suroccidente"},
        {"NOMBRE": "Anuar Javier Contreras Olivera", "CARGO": "Ejecutivo de Cuenta", "Regional": "Norte"},
        {"NOMBRE": "Jeimy Carolina Salamanca Porras", "CARGO": "Ejecutivo de Cuenta", "Regional": "Centro"},
        {"NOMBRE": "Jorge Eliecer Orozco Bocanegra", "CARGO": "Ejecutivo de Cuenta", "Regional": "Centro"},
        {"NOMBRE": "Oscardy Molina Espinosa", "CARGO": "Ejecutivo de Cuenta", "Regional": "Suroccidente"},
        {"NOMBRE": "Roosvelt Alexander Sanchez Caro", "CARGO": "Ejecutivo de Cuenta", "Regional": "Noroccidente"},  
        {"NOMBRE": "Silvia Isabel Rojas Sanchez", "CARGO": "Ejecutivo de Cuenta", "Regional": "Norte"},
        {"NOMBRE": "Julian Camilo Diaz Ruiz", "CARGO": "Ejecutivo de Cuenta JR", "Regional": "Noroccidente"},
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
        {"NOMBRE": "Javier Ferney Jimenez", "CARGO": "Jefe De Zona", "Regional": "Centro"},
        {"NOMBRE": "Lina Maria Gonzalez Grisales", "CARGO": "Jefe De Zona", "Regional": "Centro"},
        {"NOMBRE": "Julian Medina", "CARGO": "Jefe De Zona", "Regional": "Centro"},
        {"NOMBRE": "Tulio Cesar Muriel Duran", "CARGO": "Jefe De Zona", "Regional": "Noroccidente"},
        {"NOMBRE": "Yessica Andrea Fonseca Lara", "CARGO": "Jefe De Zona", "Regional": "Centro"},
        {"NOMBRE": "Yudi Milena Pineros Garcia", "CARGO": "Jefe De Zona", "Regional": "Centro"},
        {"NOMBRE": "Luis Angel Ramirez Garces", "CARGO": "Jefe De Zona", "Regional": "Norte"},
        {"NOMBRE": "Cristhian Camilo Penagos Montaño", "CARGO": "Jefe De Zona", "Regional": "Suroccidente"},
        {"NOMBRE": "Angie Daniela Prieto Velasquez", "CARGO": "Jefe De Zona", "Regional": "Centro"},
        {"NOMBRE": "Maria Shirey Quintero", "CARGO": "Jefe De Zona", "Regional": "Norte"},
        {"NOMBRE": "Edinson Enrique Oliveros", "CARGO": "Jefe De Zona", "Regional": "Norte"},
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
            "1. ¿Transforma las características del producto en beneficios tangibles para el cliente?": ["Excelente", "Sobresaliente", "Bueno", "Por Mejorar", "No Presenta la Competencia"],
            "2. ¿Durante el proceso de venta, realiza demostraciones efectivas del producto? (Experiencia)": ["Excelente", "Sobresaliente", "Bueno", "Por Mejorar", "No Presenta la Competencia"],
            "3. ¿Maneja las objeciones de los clientes y dirige la conversación hacia el cierre de la venta?": ["Excelente", "Sobresaliente", "Bueno", "Por Mejorar", "No Presenta la Competencia"],
            "4. ¿Tiene conocimiento actualizado sobre las ofertas, precios y características de los productos de la competencia?": ["Excelente", "Sobresaliente", "Bueno", "Por Mejorar", "No Presenta la Competencia"],
            "5. ¿Mantiene los productos, el material POP y el área de exhibición en óptimas condiciones, siguiendo los lineamientos de la empresa?": ["Excelente", "Sobresaliente", "Bueno", "Por Mejorar", "No Presenta la Competencia"],
            "6. ¿Maneja cifras y terminos clave del punto de venta (como Market Share, TAM, Proyeccion y Cumplimiento) y las utiliza para tomar decisiones?": ["Excelente", "Sobresaliente", "Bueno", "Por Mejorar", "No Presenta la Competencia"],
            "7. ¿Diligencia correctamente los formularios y planillas de la carpeta comercial?": ["Excelente", "Sobresaliente", "Bueno", "Por Mejorar", "No Presenta la Competencia"],
            "8. ¿Atiende de manera oportuna y respetuosa las solicitudes de clientes internos y externos?":["Excelente", "Sobresaliente", "Bueno", "Por Mejorar", "No Presenta la Competencia"],
            "9. ¿Comunica de forma clara y puntual las novedades y/o solicitudes que surgen en su labor diaria?":["Excelente", "Sobresaliente", "Bueno", "Por Mejorar", "No Presenta la Competencia"],
            "10. ¿Cumple con las encuestas diarias de Mototalk?":["Excelente", "Sobresaliente", "Bueno", "Por Mejorar", "No Presenta la Competencia"],
            "11. ¿Mantiene una actitud proactiva y persuasiva frente al  consumidor? (abordaje efectivo)":["Excelente", "Sobresaliente", "Bueno", "Por Mejorar", "No Presenta la Competencia"],
            "12. ¿Continuaria con el promotor?": ["Sí", "No"],
            "13. El especialista tiende a tener mejor resultados cuando trabaja en":["Equipo", "Individualmente"],
            "14. ¿Identifica si el especialista tiene sentido de pertenencia hacia la marca?":["Sí", "No"],
            "15. ¿Identifica en el especialista actitudes de liderazgo que lo destaquen entre sus compañeros?":["Sí", "No"]
        }


        # Definir los rangos para cada sección
        secciones = {
            "DESEMPEÑO Y CONOCIMIENTO DEL PRODUCTO": range(1, 5),  # Preguntas 1-4
            "PUNTO DE VENTA Y CIFRAS": range(5, 8),                # Preguntas 5-7
            "COMUNICACIÓN Y SERVICIO AL CLIENTE": range(8, 12),    # Preguntas 8-11
            "POTENCIAL": range(12, 16)                             # Preguntas 12-15
        }


        # Crear claves únicas para cada radio button - con índice forzado en 0
        contador_pregunta = 0
        for seccion, rango_preguntas in secciones.items():
            # Mostrar subtítulo de la sección
            st.markdown(f"### {seccion}")
            
            # Mostrar preguntas de esta sección
            for numero_pregunta in rango_preguntas:
                # Buscar la pregunta correspondiente
                pregunta_encontrada = None
                opciones = None
                
                for pregunta, ops in preguntas_opcion_multiple.items():
                    if pregunta.startswith(f"{numero_pregunta}."):
                        pregunta_encontrada = pregunta
                        opciones = ops
                        break
                
                if pregunta_encontrada and opciones:
                    # Mostrar la pregunta con tamaño de letra más grande
                    st.markdown(f"""
                    <div style="font-size: 20px; color: white;">
                        {pregunta_encontrada}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Agregar opción vacía al inicio
                    opciones_con_vacio = ["Seleccionar..."] + opciones
                    respuesta = st.selectbox(
                        "",  # Etiqueta vacía porque ya mostraste la pregunta arriba
                        opciones_con_vacio, 
                        index=0,
                        key=f"pregunta_{contador_pregunta}_{st.session_state.session_counter}"
                    )
                    if respuesta != "Seleccionar...":
                        respuestas[pregunta_encontrada] = respuesta
                    else:
                        respuestas[pregunta_encontrada] = None
                    
                    contador_pregunta += 1


        # Pregunta de campo abierto
        st.markdown("### COMENTARIOS ADICIONALES")
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
                        
                        # Mostrar mensaje de confirmación con detalles
                        st.balloons()
                        st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, #27ae60, #2ecc71);
                            border-radius: 15px;
                            padding: 20px;
                            margin: 20px 0;
                            text-align: center;
                            color: white;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                        ">
                            <h3 style="margin: 0 0 10px 0;">🎉 ¡Evaluación Enviada Exitosamente!</h3>
                            <p style="margin: 5px 0; font-size: 16px;">
                                La evaluación del promotor ha sido registrada correctamente en el sistema.
                            </p>
                            <p style="margin: 5px 0; font-size: 14px;">
                                Gracias por completar la evaluación.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Incrementar contador de sesión para resetear el formulario
                        st.session_state.session_counter += 1
                        time.sleep(3)
                        st.rerun()
                        
                    elif registros_exitosos > 0:
                        st.warning(f"⚠️ Se guardaron {registros_exitosos} de {len(filas)} respuestas. Revisa los errores anteriores.")
                    else:
                        st.error("❌ No se pudo guardar ninguna respuesta. Intenta nuevamente.")


# Footer siempre visible
st.markdown("""
<hr style="border:1px solid #ccc; margin-top:40px;">

<div style='text-align: center; font-size: 12px; color: gray;'>
Desarrollado por <strong> Dairon Manuel Alonso Herrera </strong> - Desarrollador BI y <strong> Manuel Esteban Pimentel Alvarez </strong> - Analista BI Adecco BPO Colombia<br>
© 2025 Todos los derechos reservados
</div>
""", unsafe_allow_html=True)
