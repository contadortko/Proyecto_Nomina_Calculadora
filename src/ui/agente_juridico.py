# src/ui/consulta_legal.py
import streamlit as st
from datetime import date
from src.core.parametros_dian import obtener_constantes_nomina, obtener_divisor_operativo

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
            {"Concepto": "Recargo Diurno Dominical/Festivo", "Factor": f"{recargos['rdf']:.2f}", "Recargo": f"{round(recargos['rdf']*100)}%"},
            {"Concepto": "Hora Extra Diurna Dominical/Festivo", "Factor": f"{recargos['heddf']:.2f}", "Recargo": f"{round((recargos['heddf']-1)*100)}%"},
            {"Concepto": "Extra Nocturna Dominical/Festivo", "Factor": f"{recargos['hendf']:.2f}", "Recargo": f"{round((recargos['hendf']-1)*100)}%"},
            {"Concepto": "Recargo Nocturno Dominical/Festivo", "Factor": f"{recargos['rndf']:.2f}", "Recargo": f"{round((recargos['rndf']-1)*100)}%"}
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

    

    # --- BIBLIA LEGAL ADICIONAL (ACORDEONES 1072 y 1625) ---
    st.markdown("---")
    st.subheader("📖 Reglamentación Extendida (Decretos 1072 y 1625)")
    
    with st.expander("🧾 1. Retención en la Fuente y Deducciones (Procedimiento 1)"):
        st.markdown("""
        **Depuración Base Gravable (Art. 383 E.T.):**
        * **Ingresos No Constitutivos de Renta (INCRGO):** Aportes obligatorios a Salud, Pensión y Fondo de Solidaridad.
        * **Deducciones Permitidas:**
          * **Dependientes Económicos:** 10% de los ingresos brutos (Máx. 32 UVT/mes).
          * **Medicina Prepagada:** Máx. 16 UVT/mes.
          * **Intereses de Vivienda:** Máx. 100 UVT/mes.
        * **Rentas Exentas Automáticas:** 25% del subtotal depurado (Limitado estrictamente a 790 UVT anuales).
        * **Límite Cedular Total:** La suma de todas las deducciones y rentas exentas no puede superar el 40% del ingreso neto (o 1340 UVT anuales).
        """)

    with st.expander("🛡️ 2. Límites UGPP y Gastos No Constitutivos de Salario"):
        st.markdown("""
        **La Regla del 40% (Art. 30, Ley 1393 de 2010):**
        * Si empresa y empleado pactan auxilios (ej. Rodamiento, alimentación, bonos extralegales) por mutuo acuerdo calificados como *No Constitutivos de Salario*.
        * **Tope Máximo:** La suma de todos estos pagos no salariales **nunca podrá exceder el 40% del total de la remuneración mensual**.
        * Si excede este límite, el porcentaje sobrante hace base inmediata para liquidar Seguridad Social, Parafiscales y Riesgos.
        * **Viáticos:** Solo los viáticos permanentes de manutención y alojamiento constituyen salario (excluyen transporte/gastos de representación).
        """)

    with st.expander("⚖️ 3. Indemnizaciones y Reglas de Contratistas (Laboral/Civil)"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            **Indemnizaciones (Despido Injusto):**
            * **Término Fijo / Obra Labor:** Se paga el 100% de los salarios correspondientes al tiempo o labor que faltaba por cumplir (Mínimo 15 días).
            * **Término Indefinido (Sueldo < 10 SMMLV):** 30 días de salario por el primer año + 20 días por cada año adicional.
            * **Término Indefinido (Sueldo > 10 SMMLV):** 20 días por el primer año + 15 días por cada año adicional.
            """)
        with c2:
            st.markdown("""
            **Contratistas (Independientes por Honorarios):**
            * El Ingreso Base de Cotización (IBC) está fijado sobre el **40% del valor mensualizado del contrato**.
            * Deben pagar 16% Pensión y 12.5% Salud (a su cargo 100%).
            * Las empresas contratantes están obligadas a retener el 10% u 11% (ReteFuente) sobre el valor bruto del pago, según sus responsabilidades tributarias.
            """)
            
    # --- BLOQUE DE ALERTAS Y NOTIFICACIONES ---
    st.markdown("---")
    st.subheader("📢 Notificaciones de Gestión Operativa")
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