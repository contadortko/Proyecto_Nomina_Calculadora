import streamlit as st
from datetime import date
from src.core.groq_client import get_groq_client, consultar_groq
from src.core.parametros_dian import obtener_constantes_nomina, obtener_divisor_operativo
import os
from src.core.conocimiento_legal import MARCO_JURIDICO_COLOMBIANO

def obtener_contexto_sistema(modo):
    fecha_hoy = date.today()
    parametros = obtener_constantes_nomina(fecha_hoy)
    divisor = obtener_divisor_operativo(fecha_hoy)
    
    if "Liquidador" in modo:
        rol = "un Liquidador Senior de Nómina y Matemático Exhaustivo"
        personalidad = "Reglas Fijas de Cálculo:\n1. NUNCA asumas valores; si el usuario omite el salario de un empleado mínimo, usa estrictamente el SMMLV divulgado abajo.\n2. Extrae obligatoriamente el Valor Hora Ordinaria (VHO) = Salario Base / Divisor Operativo.\n3. Desglosa mostrando la fórmula directa: `Cantidad x VHO x Factor de Ley`.\n4. Muestra SIEMPRE el Subtotal y Total a Pagar en valores monetarios netos en negritas explícitas.\n5. Tono estricto, imperativo y contable. PROHIBIDÍSIMO usar términos como 'creo', 'tal vez', 'aproximadamente' o dudar."
    else:
        rol = "un Magistrado Laboral, Auditor Forense Corporativo y Asesor Tributario Implacable"
        personalidad = "Reglas Fijas de Dictamen:\n1. NO des rodeos diplomáticos. Inicia respondiendo siempre 'SÍ', 'NO' o 'RIESGO ALTO' a cualquier viabilidad legal o escenario.\n2. Si hay un 'hueco' o escudo tributario para ahorrarle cargas patronales a la empresa, revélalo táctica y asertivamente.\n3. Tienes prohibido sugerir 'consultar a un humano experto'. Asume que tú eres la máxima corte de Colombia sobre esa decisión."
        
    contexto = f"""DIRECTIVA DE ENFOQUE TEMÁTICO (CORTAFUEGOS FLEXIBLE):
Eres un experto enfocado UNICAMENTE en: Nómina, Derecho Laboral Colombiano, Tributación, Deducciones, Salarios y afines.
REGLA 1: Si el usuario te pregunta "¿Qué sabes hacer?", "quién eres" o te saluda, preséntate amablemente explicando que eres un Sistema experto de Nómina e indícale de qué temas le puedes hablar.
REGLA 2: Si te hacen una pregunta COMPLETAMENTE ajena a tu especialidad (ej. recetas de cocina, farándula, historia antigua, código Python puro o leyes extranjeras) y que no guarda ninguna relación semántica ni con nómina, salarios o empleos, debes declinar diciendo EXACTAMENTE: "No fui entrenado para eso. Por favor, intenta realizar únicamente preguntas laborales, salariales o tributarias sobre el sistema colombiano."
REGLA 3: Si la pregunta usa palabras como nómina, laboral, tributarías, deducción, salario o cualquier sinónimo indirecto (ej: "¿Cómo calculo mis pagos?"), respóndela integralmente como experto.

Actúas total y exclusivamente como {rol} en el sistema Nómina Intelligence Hub Colombia.
{personalidad}

{MARCO_JURIDICO_COLOMBIANO}

PARÁMETROS JURÍDICOS INYECTADOS HOY ({fecha_hoy}):
- Salario Mínimo (SMMLV): ${parametros['smmlv']}
- Auxilio de Transporte Obligatorio: ${parametros['aux_transporte']}
- Factor Divisor Operativo (Ley 2101): {divisor} al mes.
- Valor Referencial UVT: ${parametros.get('uvt', 47065)}

INSTRUCCIÓN CRÍTICA: Eres implacable y estructurado. Responde diagramando con viñetas, resultados precisos o tablas contables, evitando cualquier saludo robótico."""
    return contexto

def inicializar_historial_groq():
    if "groq_messages" not in st.session_state:
        st.session_state.groq_messages = []

def exportar_chat_txt():
    texto = "========================================================\n"
    texto += "  REPORTE DE AUDITORÍA Y PLANEACIÓN (STATELESS NUBE GROQ)\n"
    texto += "              NÓMINA INTELLIGENCE HUB                    \n"
    texto += f"              Fecha de Cierre: {date.today()}        \n"
    texto += "========================================================\n\n"
    for msg in st.session_state.groq_messages:
        rol = "🗣 USUARIO" if msg["role"] == "user" else "⚡ AGENTE IA (GROQ)"
        texto += f"{rol}:\n{msg['content']}\n\n{'-'*56}\n\n"
    return texto

def renderizar_agente_groq():
    inicializar_historial_groq()
    
    from dotenv import load_dotenv
    load_dotenv()
    
    env_key = ""
    try:
        env_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass
        
    if not env_key:
        env_key = os.getenv("GROQ_API_KEY", "")
        
    if not env_key:
        st.error("⚠️ Sistema fuera de línea: Servidor de IA desconectado.")
        return
        
    cliente = get_groq_client(env_key)
    if not cliente:
        st.error("Error al arrancar los hilos de red LPU.")
        return
    
    # Motor fijado internamente (Sin UI)
    modelo_seleccionado = "llama" 
    modo_ia = "Liquidador" # Se asume en todo el programa
    
    if st.session_state.groq_messages:
        reporte_txt = exportar_chat_txt()
        st.download_button(
            label="📥 Bajar Historial (.txt)",
            data=reporte_txt,
            file_name=f"Auditoria_{date.today()}.txt",
            mime="text/plain",
            use_container_width=True,
            type="primary"
        )
            
    with st.container():
        # 1. Caja de chat siempre visible y anclada al tope de la rutina
        if prompt := st.chat_input("Escribe tu duda sobre nómina o impuestos..."):
            st.session_state.groq_messages.append({"role": "user", "content": prompt})
            
            with st.spinner("Procesando consulta..."):
                context = obtener_contexto_sistema(modo_ia)
                res = consultar_groq(cliente, st.session_state.groq_messages, modelo=modelo_seleccionado, contexto_sistema=context)
                st.session_state.groq_messages.append({"role": "assistant", "content": res})
            # Refresca agresivamente para renderizar arriba
            st.rerun()

        # 2. Visualización INVERSA: Desde la última hasta la primera
        for message in reversed(st.session_state.groq_messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
