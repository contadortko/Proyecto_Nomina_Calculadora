import streamlit as st
from datetime import date
from src.ui.calculadora import mostrar_calculadora
from src.ui.consulta_legal import renderizar_modulo_legal 
from src.core.base_legal import obtener_constantes_nomina, obtener_divisor_operativo

# 1. CONFIGURACIÓN RESPONSIVA
st.set_page_config(
    page_title="Nomina Intelligence Hub Colombia", 
    layout="wide", # Clave para que use todo el ancho de la pantalla
    initial_sidebar_state="expanded" # En móviles, la barra lateral inicia cerrada para ganar espacio
)

def main():
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

    # --- ESTILOS RESPONSIVOS (CSS) ---
    st.markdown("""
        <style>
        [data-testid="stMetricValue"] { font-size: 1.8rem; }
        .stTable { width: 100%; }
        @media (max-width: 640px) {
            [data-testid="stMetricValue"] { font-size: 1.2rem; }
        }
        </style>
    """, unsafe_allow_html=True)

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

        # FILA 2: TABLAS (Uso de columnas que se apilan en móviles)
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📋 Recargos y Horas Extras")
            # Tabla completa y dinámica
            st.markdown(f"""
            | Concepto | % | Factor |
            | :--- | :---: | :---: |
            | H. Extra Diurna | 25% | 1.25 |
            | H. Nocturna | 35% | 0.35 |
            | H. Extra Nocturna | 75% | 1.75 |
            | Recargo Dom/Fest | 75% | 1.75 |
            | Extra Diurna D/F | 100% | 2.00 |
            | Extra Nocturna D/F| 150% | 2.50 |
            | Recargo Noct. D/F | 110% | 2.10 |
            """)
            st.info(f"Divisor actual para cálculos: **{divisor}** (Basado en fecha)")

        with col2:
            st.subheader("🏦 Estructura de Costos y Aportes")
            # Segmentación solicitada en pestañas responsivas
            tab1, tab2, tab3, tab4 = st.tabs(["Prestaciones", "Seg. Social", "Rangos FSP", "Niveles ARL"])
            
            with tab1:
                st.write("""
                - **Cesantías:** 8.33%
                - **Int. Cesantías:** 1.00%
                - **Prima:** 8.33%
                - **Vacaciones:** 4.17%
                """)
            
            with tab2:
                st.write("""
                - **Salud:** 4% (Empleado) / 8.5% (Patrón*)
                - **Pensión:** 4% (Empleado) / 12% (Patrón)
                - **Caja Compensación:** 4% (Patrón)
                - **Sena/ICBF:** 2% / 3% (Patrón*)
                - **Exoneración:** Ley 1607 si < 10 SMMLV.
                """)

                # --- MENSAJE DE ACLARACIÓN TÉCNICA ---
                st.info("""
                **(*) Nota de Exoneración (Art. 114-1 E.T.):** Las sociedades están exoneradas del pago de aportes a **SENA, ICBF y Salud** por los empleados que devenguen, individualmente considerados, menos de **10 SMMLV** ($17.059.050).
                """)
            
            with tab3:
                st.markdown("""
                | IBC (en SMMLV) | Tarifa FSP |
                | :--- | :---: |
                | 4 a < 16 | 1.0% |
                | 16 a 17 | 1.2% |
                | 17 a 18 | 1.4% |
                | 18 a 19 | 1.6% |
                | 19 a 20 | 1.8% |
                | > 20 | 2.0% |
                """)

            with tab4:
                st.markdown("""
                | Clase | Riesgo | Tarifa |
                | :--- | :--- | :---: |
                | I | Mínimo | 0.522% |
                | II | Bajo | 1.044% |
                | III | Medio | 2.436% |
                | IV | Alto | 4.350% |
                | V | Máximo | 6.700% |
                """)

        # FILA 3: ALERTAS LEGALES
        st.markdown("---")
        c_alert, c_status = st.columns([2, 1])
        with c_alert:
            if not es_post_julio:
                st.warning(f"⚠️ **Alerta Legal:** Faltan {(date(2026, 7, 1) - fecha_hoy).days} días para el cambio a 42h.")
            else:
                st.success("✅ **Ley 2101 activa:** Jornada reducida aplicada con éxito.")
        with c_status:
            st.info(f"**Ubicación:** Bogotá\n**Estado:** En desarrollo")

    
    elif "🧮 Calcular Nómina Individual" in opcion:
        mostrar_calculadora()

    elif opcion == "🔍 Consulta Legal":
        renderizar_modulo_legal()

if __name__ == "__main__":
    main()