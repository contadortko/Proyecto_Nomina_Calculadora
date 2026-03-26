import os
from dotenv import load_dotenv
from datetime import date
import streamlit as st
import pandas as pd
import io
from fpdf import FPDF

# Cargamos las variables de entorno del archivo .env
load_dotenv()

# Obtenemos la clave de forma segura
# (Asegúrate de que en tu archivo .env diga: GROQ_API_KEY=gsk_...)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# RUTAS ACTUALIZADAS PARA LA ARQUITECTURA DE CAPAS
from src.core.motor_retencion import depurar_base_laboral, calcular_retencion_final
from src.core.motor_costos_empresa import (
    calcular_auxilio_transporte, 
    calcular_provisiones_mensuales, 
    calcular_parafiscales_y_ss
)
from src.core.motor_devengos import calcular_extras, calcular_deducciones_ley, obtener_tarifa_fsp

def generar_pdf_robusto(df_em, df_pa, neto_final, costo_total_mes, base_uvt, nombre_empleado=""):
    """
    Motor nativo para generar reportes auditables en PDF.
    """
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Encabezado
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, f"REPORTE DE LIQUIDACIÓN: {nombre_empleado.upper()}", 0, 1, "C")
    pdf.ln(5)

    # Sección Costo Empresa (Usamos df_pa que es el argumento recibido)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "2. CARGA PRESTACIONAL Y PARAFISCAL (COSTO EMPRESA)", 0, 1, "L")
    pdf.set_font("Arial", "", 10)
    
    for index, row in df_pa.iterrows(): # <--- Corregido: df_pa en lugar de df_empresa
        pdf.cell(95, 8, str(row["Concepto"]), 1)
        pdf.cell(95, 8, f"$ {row['Valor']:,.0f}", 1, 1, "R")
    
    # Totales Finales
    pdf.ln(10)
    pdf.set_font("Arial", "B", 11)
    # Corregido: Usamos neto_final y costo_total_mes que son los argumentos reales
    pdf.cell(190, 8, f"BASE GRAVABLE: {base_uvt:,.2f} UVT", 0, 1, "R")
    pdf.cell(190, 8, f"NETO A RECIBIR: $ {neto_final:,.0f}", 0, 1, "R")
    pdf.cell(190, 8, f"COSTO TOTAL MENSUAL: $ {costo_total_mes:,.0f}", 0, 1, "R")
    
    return bytes(pdf.output())

def mostrar_calculadora():

    def formato_contable(valor):
        """Formato: (1.000) para negativos, 1.000 para positivos, vacío para NaN/None"""
        if pd.isna(valor) or valor is None:
            return ""
        if valor < 0:
            # Importante: f-string con paréntesis por fuera del valor absoluto
            return f"({abs(valor):,.0f})"
        return f"{valor:,.0f}"

    # 1. Creamos dos columnas: una ancha para el título y una pequeña para la fecha
    col_titulo, col_fecha = st.columns([3, 1])

    with col_titulo:
        st.title("🛡️ Proceso de nómina Individual")
    
    from src.core.parametros_dian import HISTORICO_LEGAL
    max_year = max(HISTORICO_LEGAL.keys())
    
    with col_fecha:
        # Ubicamos el selector limitando los horizontes (No antes de 2026, ni después de los datos vigentes)
        fecha_nomina = st.date_input(
            "Periodo de Liquidación", 
            value=date.today(),
            min_value=date(2026, 1, 1),
            max_value=date(max_year, 12, 31),
            help="El sistema bloquea periodos anteriores al 2026 o años sin parámetros legales oficiales aprobados."
        )
    
    # INYECCIÓN DINÁMICA: Carga de parámetros desde el cerebro legal según la fecha
    from src.core.parametros_dian import obtener_constantes_nomina
    parametros_legales = obtener_constantes_nomina(fecha_nomina)
    smmlv_dinamico = parametros_legales['smmlv']
    uvt_dinamica = parametros_legales.get('uvt', 52374)
    aux_transporte_dinamico = parametros_legales['aux_transporte']
    
    with st.sidebar:
        st.header("⚙️ Configuración Global")

        es_integral = st.toggle("Salario Integral")
        metodo = st.radio("Procedimiento Rete", [1, 2])
        pct_fijo = st.number_input("% Fijo (Proc 2)", 0.0) if metodo == 2 else 0.0
        exonerado_empresa = st.checkbox("Empresa Exonerada (Art. 114-1)", value=True)
        nivel_arl = st.selectbox(
            "Nivel de Riesgo ARL", 
            ["Riesgo I (0.522%)", "Riesgo II (1.044%)", "Riesgo III (2.436%)", "Riesgo IV (4.350%)", "Riesgo V (6.960%)"],
            help="Seleccione según la actividad económica de la empresa"
        )

    # Extraemos nuevos diccionarios del cerebro legal
    porcentajes_ss = parametros_legales['porcentajes_ss']
    topes_uvt = parametros_legales['topes_dian_uvt']

    st.markdown("### 👤 Datos del Empleado")
    nombre_empleado = st.text_input("Nombre Completo (Opcional - Usado en reportes)", placeholder="Ej. Juan Pérez")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["💵 Carga Salarial (Devengos)", "⚖️ Depuración DIAN (Retención)", "📉 Préstamos y Terceros"])
    
    with tab1:
        st.subheader("💰 Tiempo y Devengos Base")
        
        # Fila 1: Sueldo y Días
        col_s1, col_s2, col_s3 = st.columns(3)
        sueldo_pactado = col_s1.number_input("Sueldo Mensual Full", value=float(smmlv_dinamico))
        dias_lab = col_s2.number_input("Días Laborados", 1, 30, value=30)
        dias_aus = col_s3.number_input("Días Ausencia/LNNR", 0, 30, value=0)
        
        sueldo_proporcional = round((sueldo_pactado / 30) * (dias_lab - dias_aus), 0)
        st.info(f"Liquidando proporcionalmente sobre **{dias_lab - dias_aus}** días efectivos laborales.")

        # Fila 2: Comisiones y Bonos
        col_b1, col_b2, col_b3 = st.columns(3)
        comisiones = col_b1.number_input("Comisiones Ganadas", 0.0)
        bono_pres = col_b2.number_input("Bonos Prestacionales", 0.0)
        bono_no_pres = col_b3.number_input("Bonos NO Prestacionales (Ojo Regla 40%)", 0.0)

        with st.expander("🕒 Horas Extras y Recargos (cantidad en horas)"):
            from src.core.parametros_dian import obtener_tabla_recargos
            p_extras = obtener_tabla_recargos(fecha_nomina)
            
            # Sub-columnas para evitar campos muy largos en extras
            c_ex1, c_ex2, c_ex3 = st.columns(3)
            with c_ex1:
                hed = st.number_input(f"Extra Diurna ({p_extras['hed']})", 0)
                hen = st.number_input(f"Extra Nocturna ({p_extras['hen']})", 0)
                rn = st.number_input(f"Recargo Nocturno ({p_extras['rn']})", 0)
            with c_ex2:
                heddf = st.number_input(f"Extra Diurn. Dom ({p_extras['heddf']})", 0)
                hendf = st.number_input(f"Extra Noct. Dom ({p_extras['hendf']})", 0)
            with c_ex3:
                rdf = st.number_input(f"Recargo Dom ({p_extras['rdf']})", 0)
                rndf = st.number_input(f"Rec. Noct. Dom ({p_extras['rndf']})", 0)

            dict_extras = {
                "hed": hed, "hen": hen, "heddf": heddf, "hendf": hendf,
                "rn": rn, "rdf": rdf, "rndf": rndf
            }
            # Calculamos inmediatamente para la base
            detalle_ext, total_ext, div_usado = calcular_extras(sueldo_pactado, dict_extras, fecha_nomina)

    with tab2:
        st.subheader("📉 Depuración Tributaria (Retención de Ley)")
        
        col_trib1, col_trib2 = st.columns(2)
        
        with col_trib1:
            st.markdown("#### ➖ Deducciones y Aportes")
            vol_obl = st.number_input("Aportes Voluntarios a Obligatorios (RAIS)", 0.0)
            viv = st.number_input("Intereses de Vivienda (Art. 119)", 0.0)
            if viv > (topes_uvt["vivienda_mensual"] * uvt_dinamica):
                st.warning(f"⚠️ Limitado a tope DIAN de {topes_uvt['vivienda_mensual']} UVT.")
                
            med = st.number_input("Salud Prepagada (Art. 387)", 0.0)
            if med > (topes_uvt["medicina_prepagada_mensual"] * uvt_dinamica):
                st.warning(f"⚠️ Limitado a tope DIAN de {topes_uvt['medicina_prepagada_mensual']} UVT.")

            dep = st.checkbox('¿Tiene derecho a deducción por dependientes?')
            if dep:
                st.success(f"✅ Deducción automática del 10% (Máx {topes_uvt['dependientes_mensual']} UVT).")

        with col_trib2:
            st.markdown("#### 🛡️ Rentas Exentas")
            fvp = st.number_input("Aportes a Pensiones Voluntarias (FVP)", 0.0)
            afc = st.number_input("Aportes a cuentas AFC / AVC", 0.0)
            ind_accidente = st.number_input("Indemnizaciones Ley (Art 206 Num 1-3)", 0.0)
            otras_ex = st.number_input("Otras rentas exentas", 0.0)

    with tab3:
        st.subheader("📎 Otras Deducciones de Nómina")
        col_ded1, col_ded2, col_ded3 = st.columns(3)
        libranzas = col_ded1.number_input("Cuotas Libranzas", 0.0)
        embargos = col_ded2.number_input("Embargos de Ley", 0.0)
        cuotas_otros = col_ded3.number_input("Cuotas Sindicatos / Otras", 0.0)

    # --- MOTOR DE CÁLCULO REACTIVO ---
    base_salarial = sueldo_proporcional + comisiones + total_ext + bono_pres
    ibc_ss = base_salarial * 0.7 if es_integral else base_salarial
    
    # Obtenemos las deducciones fijas (Salud y Pensión) inyectando diccionarios
    salud_e, pension_e = calcular_deducciones_ley(ibc_ss, smmlv_dinamico, porcentajes_ss)
    fsp, tasa_fsp_decimal = obtener_tarifa_fsp(ibc_ss, smmlv_dinamico)
    
    ded_dict = {'medicina': med, 'vivienda': viv, 'dependientes': dep, 'pension_vol_obl': vol_obl}
    exe_dict = {'afc': afc, 'fvp': fvp, 'art206': {'otras': otras_ex + ind_accidente}}
    
    # Inyección de topes de la DIAN a la función purista
    base_uvt, base_grav_pesos = depurar_base_laboral(base_salarial, salud_e, pension_e, fsp, ded_dict, exe_dict, uvt_dinamica, topes_uvt)
    rete = calcular_retencion_final(base_uvt, uvt_dinamica, metodo, pct_fijo)

    aux_t = calcular_auxilio_transporte(sueldo_pactado, smmlv_dinamico, aux_transporte_dinamico) if not es_integral else 0
    aux_t_prop = round((aux_t / 30) * (dias_lab - dias_aus), 0)
    total_devengado = base_salarial + bono_no_pres + aux_t_prop
    aplica_exo = exonerado_empresa and (min(ibc_ss, smmlv_dinamico*25) < (10 * smmlv_dinamico))
    
    prov = calcular_provisiones_mensuales(base_salarial, aux_t_prop, es_integral, dias_lab - dias_aus)
    para = calcular_parafiscales_y_ss(base_salarial, es_integral, aplica_exo, porcentajes_ss, nivel_arl)

    neto_final = total_devengado - salud_e - pension_e - fsp - rete - libranzas - embargos - cuotas_otros
    costo_total_mes = total_devengado + sum(prov.values()) + sum(para.values())

    # --- RENDERIZADO VISUAL REACTIVO ---
    st.markdown("---")
    st.subheader("📊 Análisis y Resultados (Cálculo Inmediato)")
    
    if ibc_ss >= (smmlv_dinamico * 25): st.warning(f"⚖️ IBC limitado al tope legal de 25 SMMLV")
    if aplica_exo: st.success("✅ Exonerado Art. 114-1 ET (SENA, ICBF, Salud Empleador)")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Base Gravable UVT", f"{base_uvt:,.2f}")
    m2.metric("ReteFuente DIAN", f"${rete:,.0f}")
    m3.metric("Neto a Recibir", f"${neto_final:,.0f}")
    m4.metric("Costo Real Empresa", f"${costo_total_mes:,.0f}")

    # PLOTLY CHARTS
    import plotly.graph_objects as go
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Donut Chart - Costo Empresa
        etiquetas_emp = ["Salario Bruto", "Parafiscales", "S.S. Patronal", "Provisiones (Prestaciones)"]
        sum_salario = total_devengado
        sum_paraf = para['caja_compensacion'] + para.get('sena', 0) + para.get('icbf', 0)
        sum_ss = para.get('salud_patronal', 0) + para['pension_patronal'] + para.get('arl_1', 0)
        sum_prov = sum(prov.values())
        
        fig1 = go.Figure(data=[go.Pie(labels=etiquetas_emp, values=[sum_salario, sum_paraf, sum_ss, sum_prov], hole=.4)])
        fig1.update_layout(title_text="Distribución Costo Empresa Mensual", showlegend=True, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        # Waterfall Chart - Bruto a Neto
        fig2 = go.Figure(go.Waterfall(
            name="Neto", orientation="v",
            measure=["relative", "relative", "relative", "relative", "total"],
            x=["Devengado", "Salud (4%)", "Pensión (4%)", "Retefuente", "NETO"],
            textposition="outside",
            text=[f"${total_devengado:,.0f}", f"-${salud_e:,.0f}", f"-${pension_e:,.0f}", f"-${rete:,.0f}", f"${neto_final:,.0f}"],
            y=[total_devengado, -salud_e, -pension_e, -rete, 0],
            connector={"line":{"color":"rgb(63, 63, 63)"}}
        ))
        fig2.update_layout(title="Cascada: Bruto a Neto", showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig2, use_container_width=True)

    # --- TABLAS DE AUDITORIA ---
    with st.expander("📄 Ver Tablas de Auditoría y Exportar"):
        df_em = pd.DataFrame([
            ("Sueldo Proporcionado", sueldo_proporcional),
            ("Horas extras y recargos", total_ext),
            ("Auxilio de Transporte", aux_t_prop),
            ("Comisiones / Bonos", comisiones + bono_pres + bono_no_pres),
            ("Aporte Salud", -salud_e),
            ("Aporte Pensión", -pension_e),
            (f"Aporte FSP ({tasa_fsp_decimal*100:.1f}%)", -fsp),
            ("ReteFuente", -rete),
            ("Otras Deducciones (Libranza/Embargo)", -(libranzas + embargos + cuotas_otros)),
        ], columns=["Concepto", "Valor"])

        df_pa = pd.DataFrame([
            ("Salud Patronal", para.get('salud_patronal', 0)),
            ("Pensión Patronal", para['pension_patronal']),
            (f"ARL", para.get('arl_1', 0)),
            ("Cesantías", prov.get('cesantias', 0)),
            ("Intereses de Cesantías", prov.get('intereses_cesantias', 0)),
            ("Prima", prov.get('prima', 0)),
            ("Vacaciones", prov.get('vacaciones', 0)),
            ("Caja", para['caja_compensacion']),
            ("SENA/ICBF", para.get('sena', 0) + para.get('icbf', 0)),
        ], columns=["Concepto", "Valor"])

        col_t1, col_t2 = st.columns(2)
        col_t1.dataframe(df_em[df_em["Valor"] != 0].style.format({"Valor": formato_contable}), hide_index=True)
        col_t2.dataframe(df_pa[df_pa["Valor"] != 0].style.format({"Valor": formato_contable}), hide_index=True)

        st.markdown("---")
        st.subheader("📥 Exportación de Reportes Dinámicos")
        col_formato, col_boton = st.columns([2, 1])
        
        opcion_formato = col_formato.selectbox(
            "Seleccione el formato de extracción requerido",
            ["PDF (Reporte Ejecutivo Auditado)", "Excel (.xlsx - Matriz Contable)", "CSV (.csv - Plano de Datos)"],
            label_visibility="collapsed"
        )
        
        # Limpiamos el nombre para el archivo
        nombre_safe = nombre_empleado.strip().replace(' ', '_') if nombre_empleado else "general"
        
        if "PDF" in opcion_formato:
            pdf_bytes = generar_pdf_robusto(df_em, df_pa, neto_final, costo_total_mes, base_uvt, nombre_empleado)
            col_boton.download_button("Descargar Archivo 📄", pdf_bytes, f"auditoria_laboral_{nombre_safe}.pdf", mime="application/pdf", use_container_width=True)
            
        elif "Excel" in opcion_formato:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                hoja_empleado = nombre_safe[:30] if nombre_safe != "general" else "Empleado"
                df_em.to_excel(writer, sheet_name=hoja_empleado, index=False)
                df_pa.to_excel(writer, sheet_name='Costos_Empresa', index=False)
            col_boton.download_button("Descargar Archivo 📊", buf.getvalue(), f"matriz_contable_{nombre_safe}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            
        elif "CSV" in opcion_formato:
            df_concat = pd.concat([df_em, df_pa], keys=["Devengos_Deducciones", "Provisiones_Empresa"]).reset_index(level=0)
            df_concat.rename(columns={'level_0': 'Clasificacion'}, inplace=True)
            csv_data = df_concat.to_csv(index=False).encode('utf-8')
            col_boton.download_button("Descargar Archivo 💾", csv_data, f"plano_datos_{nombre_safe}.csv", mime="text/csv", use_container_width=True)
