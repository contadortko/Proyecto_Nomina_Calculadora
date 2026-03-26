import streamlit as st
from datetime import date
from src.ui.calculadora_individual import mostrar_calculadora
from src.ui.agente_juridico import renderizar_modulo_legal 
from src.core.parametros_dian import obtener_constantes_nomina, obtener_divisor_operativo
from src.ui.agente_groq import renderizar_agente_groq

# 1. CONFIGURACIÓN RESPONSIVA
st.set_page_config(
    page_title="Nomina Intelligence Hub Colombia", 
    layout="wide", # Clave para que use todo el ancho de la pantalla
    initial_sidebar_state="expanded" # En móviles, la barra lateral inicia cerrada para ganar espacio
)

def main():
    # --- CABECERA FLOTANTE (IA SIEMPRE VISIBLE) ---
    c_espacio, c_ia = st.columns([8, 2])
    with c_ia:
        with st.popover("🤖 Agente IA", use_container_width=True):
            renderizar_agente_groq()

    # --- LÓGICA DE AUTOMATIZACIÓN POR FECHA (LEY 2101) ---
    fecha_hoy = date.today()
    parametros_actuales = obtener_constantes_nomina(fecha_hoy)
    
    # IMPORTANTE: Usamos la función oficial para no tener fechas regadas por todo el código
    divisor = obtener_divisor_operativo(fecha_hoy)
    
    # La jornada depende directamente del divisor obtenido
    jornada_nombre = "42 Horas (Ley 2101)" if divisor == 210 else "44 Horas"
    
    # Fecha de cambio para la alerta de días restantes
    fecha_cambio = date(2026, 7, 15)
    es_post_cambio = fecha_hoy >= fecha_cambio

    # --- ESTILOS EXTERNOS (CSS) ---
    try:
        with open("src/ui/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.image("https://www.gerencie.com/wp-content/uploads/liquidacion-nomina.png", width=250)
        st.title("Gestión de Nómina")
        st.markdown("---")

        # Navegación moderna tipo menú desplegable
        opcion = st.segmented_control(
            "📍 Seleccione un Módulo:",
            options= ["🏠 Inicio / Dashboard", 
            "🧮 Calcular Nómina Individual", 
            "📊 Procesamiento Masivo", 
            "🔍 Auditoria y Validación", 
            "📝 Planeación Tributaria",
            "🔍 Consulta Legal",
            "⚙️ Configuración"],
            selection_mode="single",
            default="🏠 Inicio / Dashboard"
            )
        st.markdown("---")
        st.caption("🚀 **Versión:** 1.0.5")
        st.caption("👤 **Desarrollado por:** Anuar Monterrosa")
        st.caption("📅 **Última actualización:** 24/03/2026")

    # --- CONTENIDO PRINCIPAL ---
    if "🏠 Inicio / Dashboard" in opcion:
        st.header("Bienvenido a tu agente de Nómina")
        st.title("🚀 Panel de Control")
        
        # FILA 1: MÉTRICAS (Auto-responsivas en Streamlit)
        m1, m2, m3, m4, m5= st.columns([1,1,1,1,1])
        m1.metric("SMMLV", f"${parametros_actuales['smmlv']:,}")
        m2.metric("Aux. Transporte", f"${parametros_actuales['aux_transporte']:,}")
        m3.metric("UVT", f"${parametros_actuales['uvt']:,}")
        m4.metric("Jornada Activa", jornada_nombre)
        m5.metric("Salario Integral", "$22.176.765")

        st.markdown("---")

        # NUEVO DISEÑO INICIO (STATELESS)
        st.subheader("💡 Flujo de Trabajo y Privacidad")
        st.info("🔒 **Cero Persistencia (Stateless):** Nomina Intelligence Hub no almacena historial ni datos de empleados en la nube. Los cálculos se procesan mediante LPU en milisegundos y son destruidos de la memoria. Sube tus casos de forma confidencial.")
        
        col_c, col_d, col_e = st.columns(3)
        with col_c:
            st.success("1️⃣ Ingresa tu consulta arriba en la IA.")
        with col_d:
            st.warning("⚡ Inferencia Legal Inmediata (Groq LPU).")
        with col_e:
            st.error("📥 Ejecución y borrado de huella digital.")
            
        st.markdown("---")
        st.subheader("🚀 Pídele esto al Agente...")
        st.markdown("Copia y usa estas plantillas en el chat de arriba a la derecha para desafiar al Hub:")
        
        t1, t2 = st.columns(2)
        with t1:
            st.code('Audita la liquidación de un trabajador que laboró 15 horas extras nocturnas ganando $3.000.000 en enero.', language='markdown')
            st.code('Soy contratista civil, y cobro honorarios por $6.000.000. ¿Cuál es mi retención y seguridad social?', language='markdown')
        with t2:
            st.code('Trabajador a 1 SMMLV que se enferma por 10 días. ¿Cómo se ve su desprendible real?', language='markdown')
            st.code('Soy un Magistrado que ganaba $15 Millones. Explícame mis exenciones y calcula mi renta líquida.', language='markdown')

        # FILA 3: ALERTAS LEGALES
        st.markdown("---")
        c_alert, c_status = st.columns([2, 1])
        with c_alert:
            if not es_post_cambio:
                st.warning(f"⚠️ **Alerta Legal:** Faltan {(date(2026, 7, 1) - fecha_hoy).days} días para el cambio a 42h.")
            else:
                st.success("✅ **Ley 2101 activa:** Jornada reducida aplicada con éxito.")
        with c_status:
            st.info(f"**Ubicación:** Bogotá\n**Estado:** En desarrollo")

    
    elif "🧮 Calcular Nómina Individual" in opcion:
        mostrar_calculadora()

    elif opcion == "🔍 Consulta Legal":
        renderizar_modulo_legal()

    elif "⚙️ Configuración" in opcion:
        st.title("⚙️ Configuración y Referencia Legal")
        st.markdown("Aquí se guardan centralizadas todas las tablas brutas, matrices y porcentajes puros que usa el agente matemáticamente.")
        from src.ui.indicadores_macro import renderizar_tablas_informativas
        renderizar_tablas_informativas(divisor)

if __name__ == "__main__":
    main()