import streamlit as st

def renderizar_tablas_informativas(divisor):
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Recargos y Horas Extras")
        # Tabla completa y dinámica
        st.markdown(f"""
        | Concepto | % | Factor |
        | :--- | :---: | :---: |
        | H. Extra Diurna | 25% | 1.25 |
        | H. Nocturna (Ord) | 35% | 0.35 |
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
            **(*) Nota Exoneración:** Sociedades exoneradas de SENA, ICBF y Salud patronal para empleados de menos de 10 SMMLV.
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
