import streamlit as st
import pandas as pd
from src.core.parametros_dian import obtener_tabla_recargos, obtener_divisor_operativo
from datetime import date

def renderizar_tablas_informativas(divisor_actual):
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Recargos y Horas Extras")
        fecha_consulta = st.date_input("Consultar vigencia a la fecha:", date.today())
        recargos = obtener_tabla_recargos(fecha_consulta)
        divisor_simulado = obtener_divisor_operativo(fecha_consulta)
        
        datos_tabla = [
            {"Concepto": "H. Extra Diurna", "%": f"{int((recargos['hed']-1)*100)}%", "Factor": f"{recargos['hed']:.2f}"},
            {"Concepto": "H. Nocturna (Ord)", "%": f"{int((recargos['rn'])*100)}%", "Factor": f"{recargos['rn']:.2f}"},
            {"Concepto": "H. Extra Nocturna", "%": f"{int((recargos['hen']-1)*100)}%", "Factor": f"{recargos['hen']:.2f}"},
            {"Concepto": "Recargo Dom/Fest", "%": f"{int((recargos['rdf']-1)*100)}%", "Factor": f"{recargos['rdf']:.2f}"},
            {"Concepto": "Extra Diurna D/F", "%": f"{int((recargos['heddf']-recargos['rdf'])*100)}%", "Factor": f"{recargos['heddf']:.2f}"},
            {"Concepto": "Extra Nocturna D/F", "%": f"{int((recargos['hendf']-recargos['rdf'])*100)}%", "Factor": f"{recargos['hendf']:.2f}"},
            {"Concepto": "Recargo Noct. D/F", "%": f"{int((recargos['rndf']-recargos['rdf'])*100)}%", "Factor": f"{recargos['rndf']:.2f}"},
        ]
        
        df_recargos = pd.DataFrame(datos_tabla)
        # Inyección local segura para forzar el verde oscuro en el encabezado
        html_t = df_recargos.to_html(index=False, classes="stTable")
        st.markdown(f"<style>.stTable th {{ background-color: #77A464 !important; color: white !important; text-align: center; }}</style>{html_t}", unsafe_allow_html=True)
        
        st.info(f"Divisor legal proyectado: **{divisor_simulado}** (Basado en la fecha consultada)")

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
