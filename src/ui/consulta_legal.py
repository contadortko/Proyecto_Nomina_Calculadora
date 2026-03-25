# src/ui/consulta_legal.py
import streamlit as st
from datetime import date
from src.core.base_legal import obtener_constantes_nomina, obtener_divisor_operativo

def renderizar_modulo_legal():
    """
    Renderiza la interfaz de consulta de normativa legal colombiana.
    """
    st.title("📚 Información Legal de Nómina vigente")
    st.markdown("---")

    # 1. Selector de fecha compacto (usando columnas para que no ocupe todo el ancho)
    col_fecha, _ = st.columns([1, 2])
    with col_fecha:
        fecha_consulta = st.date_input(
            "Consultar normativa vigente para la fecha:", 
            value=date.today(),
            min_value=date(2020, 1, 1), # con esto el usuario no puede consultar información previa a esta fecha
            max_value=date(2100, 12, 31) # El usuario no puede consultar información futura a esta fecha.
        )
    # Obtenemos los datos del cerebro legal (base_legal.py)
    parametros = obtener_constantes_nomina(fecha_consulta)
    divisor = obtener_divisor_operativo(fecha_consulta)
    recargos = parametros["recargos"]

    

    # --- TABLAS DE VALORES ---
    col1, col2, col3 = st.columns([1.2,1.2,1.7]) # Ajustamos proporción para que la tabla de recargos tenga más espacio

    with col1:
        st.subheader("💰 Valores Base")
        # Calculamos la jornada semanal para mostrarla de forma amigable
        jornada_semanal = 42 if divisor == 210 else 44
        salario_integral = parametros['smmlv']*13
        
        st.write(f"**Salario Minimo Mensual Legal Vigente (SMMLV):** ${parametros['smmlv']:,}")
        st.write(f"**Auxilio Transporte:** ${parametros['aux_transporte']:,}")
        st.write(f"**Salario Integral (13 SMMLV):** ${salario_integral:,}")
        st.write(f"**UVT:** ${parametros['uvt']:,}")
        st.write(f"**Jornada Semanal:** {jornada_semanal} horas")
        st.write(f"**Divisor Operativo:** {divisor} horas/mes")

    with col2:
        st.subheader("⚖️ Recargos Vigentes")
        # Diccionario con los 7 recargos, calculando el % real sobre la hora ordinaria
        # Nota: Mostramos el recargo ADICIONAL (ej: 1.25 -> 25%)
        tabla_data = [
            {"Concepto": "Hora Extra Diurna", "Factor": "1.25", "Recargo": "25%"},
            {"Concepto": "Hora con recargo Nocturno", "Factor": "0.35", "Recargo": "35%"},
            {"Concepto": "Hora Extra Nocturna", "Factor": "1.75", "Recargo": "75%"},
            {"Concepto": "Recargo Diurno Dominical/Festivo", "Factor": f"{1 + recargos['rdf']:.2f}", "Recargo": f"{int(recargos['rdf']*100)}%"},
            {"Concepto": "Hora Extra Diurna Dominical/Festivo", "Factor": f"{recargos['heddf']:.2f}", "Recargo": f"{int((recargos['heddf']-1)*100)}%"},
            {"Concepto": "Extra Nocturna Dominical/Festivo", "Factor": f"{recargos['hendf']:.2f}", "Recargo": f"{int((recargos['hendf']-1)*100)}%"},
            {"Concepto": "Recargo Nocturno Dominical/Festivo", "Factor": f"{recargos['rndf']:.2f}", "Recargo": f"{int((recargos['rndf'])*100)}%"}
        ]
        
        # Mostramos la tabla SIN el índice (columna de números a la izquierda)
        st.dataframe(tabla_data, hide_index=True, use_container_width=True)

    with col3:
            st.subheader("🏦 Estructura de Costos y Aportes")
            # Segmentación en pestañas responsivas
            tab1, tab2, tab3, tab4 = st.tabs(["Prestaciones", "Seguridad Social", "Rangos FSP", "Niveles ARL"])
            
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
                | Ingreso mensual (IBC) SMMLV | Subcuenta de Solidaridad | Subcuenta de Subsiustencia | Aporte total al FSP |
                | :--- | :---: | :---: | :---: |
                | Menos de 4 | 0% | 0% | 0% |
                | >= 4 hasta 16 | 0.5% | 0.5% | 1% |
                | >= 16 hasta 17 | 0.5% | 0.7% | 1.2% |
                | >= 17 hasta 18 | 0.5% | 0.9% | 1.4% |
                | >= 18 hasta 19 | 0.5% | 1.1% | 1.6% |
                | >= 19 hasta 20 | 0.5% | 1.3% | 1.8% |
                | >= 20 | 0.5% | 1.5% | 2.0% |
                """)

            with tab4:
                st.markdown("""
                | Clase | Riesgo | Tarifa | Ejemplos de Actividades |
                | :--- | :--- | :---: | :--- |
                | I | Mínimo | 0.522% | Oficinas, bancos, actividades financieras, administrativas, educación. |
                | II | Bajo | 1.044% | Procesos de manufactura ligera (textiles), comercio al por menor, agricultura (algunos cultivos). |
                | III | Medio | 2.436% | Procesos industriales, manufactura de agujas, alcoholes, automotores, alimentos. |
                | IV | Alto | 4.350% | Transporte, servicios de vigilancia privada, procesos de manufactura pesada, aceites, vidrios. |
                | V | Máximo | 6.700% | Construcción, minería, manejo de explosivos, bomberos, trabajo en alturas. |
                """)

    

        # --- BLOQUE DE ALERTAS Y NOTIFICACIONES ---
    st.subheader("📢 Notificaciones de Gestión")
    # Mostramos las alertas que vienen de base_legal.py (Ley 2466, Ley 2101, etc.)
    for aviso in parametros.get("alertas", []):
        if "⚠️" in aviso:
            st.warning(aviso)
        elif "✅" in aviso:
            st.success(aviso)
        else:
            st.info(aviso)        

    st.divider()
    st.caption(f"Información procesada para el año fiscal {parametros['año_ejecucion']} | v1.0.5")