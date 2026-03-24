import streamlit as st
from interfaces.ui_calculadora import mostrar_calculadora

# 1. CONFIGURACIÓN DE PÁGINA PROFESIONAL
st.set_page_config(
    page_title="Nomina Intelligence Hub 2026", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

def main():
    # --- ESTILOS PERSONALIZADOS ---
    st.markdown("""
        <style>
        .main { background-color: #f5f7f9; }
        .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
        </style>
    """, unsafe_allow_html=True)

    # --- BARRA LATERAL (Navegación Intacta) ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2652/2652218.png", width=80)
        st.title("Control de Gestión")
        st.markdown("---")
        
        opcion = st.radio(
            "Módulos del Sistema:",
            ["🏠 INICIO / DASHBOARD", 
             "🧮 CALCULADORA INDIVIDUAL", 
             "📊 PROCESAMIENTO MASIVO", 
             "🔍 AUDITORÍA Y VALIDACIÓN", 
             "📝 PLANEACIÓN TRIBUTARIA", 
             "⚙️ CONFIGURACIÓN"],
            key="nav_radio"
        )
        st.markdown("---")
        st.caption("Versión 1.0.4 - Auditoría 2026")

    # --- LÓGICA DE VISUALIZACIÓN ---

    if "INICIO" in opcion:
        st.title("🚀 Panel de Control - Indicadores 2026")
        st.markdown("---")
        
        # Fila 1: Métricas Legales Actualizadas
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("SMMLV 2026", "$1.705.905")
        c2.metric("Aux. Transporte", "$249.095")
        c3.metric("UVT 2026", "$52.374")
        c4.metric("Salario Integral", "$22.176.765")
        
        st.markdown("---")
        
        # Fila 2: Información de Recargos y Alerta Legal
        col_tabla, col_info = st.columns([2, 1])
        
        with col_tabla:
            st.subheader("📋 Tabla de Recargos Vigente")
            st.write("""
            | Concepto | Recargo | Factor |
            | :--- | :---: | :--- |
            | Extra Diurno | 25% | 1.25 |
            | Nocturno | 35% | 0.35 |
            | Extra Nocturno | 80% | 1.80 |
            | Dominical/Festivo (Ene-Jun) | 80% | 1.80 |
            | Dominical/Festivo (Jul-Dic) | 90% | 1.90 |
            """)
        
        with col_info:
            st.warning("⚠️ **Recordatorio Ley 2101:**\nA partir del **15 de julio de 2026**, la jornada laboral se reduce a **42 horas semanales**. El divisor para cálculos cambia de 220 a **210 horas mensuales**.")
            st.info("**Ubicación Actual:** Bogotá, Colombia\n**Estado:** Auditoría de Retención Procedimiento 1 y 2 activa.")

    elif "CALCULADORA INDIVIDUAL" in opcion:
        # Aquí se llama a la función que ya sincronizamos con los motores core
        mostrar_calculadora()

    elif "PROCESAMIENTO MASIVO" in opcion:
        st.title("📊 Procesamiento Masivo")
        st.info("Módulo en desarrollo: Aquí podrás cargar el archivo Excel de auditoría.")

    elif "CONFIGURACIÓN" in opcion:
        st.title("⚙️ Configuración del Sistema")
        st.write("Gestión de parámetros globales y constantes UVT.")

if __name__ == "__main__":
    main()
