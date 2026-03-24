from datetime import date
import streamlit as st
import pandas as pd
import io
from fpdf import FPDF
from core.formulas_retencion import depurar_base_laboral, calcular_retencion_final
from core.formulas_prestaciones import calcular_auxilio_transporte, calcular_provisiones_mensuales, calcular_parafiscales_y_ss
from core.formulas_nomina import calcular_extras, calcular_deducciones_ley, obtener_tarifa_fsp

def generar_pdf_robusto(df_empleado, df_empresa, neto, costo_total, uvt_base):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "REPORTE GERENCIAL DE NÓMINA - AUDITORÍA 2026", 0, 1, "C")
    
    pdf.set_font("Arial", "B", 12)
    pdf.ln(5)
    pdf.cell(190, 10, f"1. RESUMEN EMPLEADO (Base Gravable: {uvt_base} UVT)", 0, 1, "L")
    pdf.set_font("Arial", "", 10)
    for index, row in df_empleado.iterrows():
        pdf.cell(95, 8, str(row["Concepto"]), 1)
        pdf.cell(95, 8, f"$ {row['Valor']:,.0f}", 1, 1, "R")
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "2. CARGA PRESTACIONAL Y PARAFISCAL (COSTO EMPRESA)", 0, 1, "L")
    pdf.set_font("Arial", "", 10)
    for index, row in df_empresa.iterrows():
        pdf.cell(95, 8, str(row["Concepto"]), 1)
        pdf.cell(95, 8, f"$ {row['Valor']:,.0f}", 1, 1, "R")
    
    pdf.set_font("Arial", "B", 10)
    pdf.ln(5)
    pdf.cell(190, 10, f"NETO A RECIBIR: $ {neto:,.0f}", 0, 1, "R")
    pdf.cell(190, 10, f"COSTO TOTAL MENSUAL: $ {costo_total:,.0f}", 0, 1, "R")
    
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
    
    with col_fecha:
        # Ubicamos el selector en la esquina superior derecha
        fecha_nomina = st.date_input(
            "Periodo de Liquidación", 
            value=date.today(), # esto siempre traerá la fecha actual, pero el usuario puede cambiarla
            help="Cambia a Julio para activar la reducción de jornada (Divisor 210)"
        )
    smmlv_2026 = 1705905
    uvt_2026 = 52374
    
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

    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("💰 Tiempo y Devengos")
        sueldo_pactado = st.number_input("Sueldo Mensual Full", value=1705905.0)
        col_d1, col_d2 = st.columns(2)
        dias_lab = col_d1.number_input("Días Laborados", 1, 30, value=30)
        dias_aus = col_d2.number_input("Días Ausencia/LNNR", 0, 30, value=0)
        sueldo_proporcional = round((sueldo_pactado / 30) * (dias_lab - dias_aus), 0)
        st.info(f"Liquidando sobre **{dias_lab - dias_aus}** días efectivos.")

        with st.expander("🕒 Horas Extras y Recargos (Cantidades)"):
            # Detectamos el escenario para mostrar la etiqueta correcta al usuario
            es_post_reforma = fecha_nomina >= date(2026, 7, 1)
    
            # Definición de etiquetas dinámicas según tu formulas_nomina.py
            f_heddf = "2.25" if es_post_reforma else "2.05"
            f_hendf = "2.75" if es_post_reforma else "2.65"
            f_rdf   = "1.90" if es_post_reforma else "1.80"
            f_rndf  = "1.25" if es_post_reforma else "1.15"

            dict_extras = {
                "hed": st.number_input("Extra Diurno (1.25)", 0),
                "hen": st.number_input("Extra Nocturno (1.75)", 0),
                "heddf": st.number_input(f"Extra Diurno D/F ({f_heddf})", 0),
                "hendf": st.number_input(f"Extra Nocturno D/F ({f_hendf})", 0),
                "rn": st.number_input("Recargo Nocturno (0.35)", 0),
                "rdf": st.number_input(f"Recargo D/F ({f_rdf})", 0),
                "rndf": st.number_input(f"Recargo Noct D/F ({f_rndf})", 0)
    }
        comisiones = st.number_input("Comisiones", 0.0)
        bono_pres = st.number_input("Bonos Prestacionales", 0.0)
        bono_no_pres = st.number_input("Bonos NO Prestacionales", 0.0)

    with c2:
        st.subheader("📉 Depuración Tributaria Completa")
        with st.expander("➕ Ingresos no constitutivos"):
            vol_obl = st.number_input("Aportes voluntarios pensión (RAIS)", 0.0)
            
        with st.expander("➖ Deducciones (Art. 387 ET)", expanded=True):
            viv = st.number_input("Intereses vivienda", 0.0)
            med = st.number_input("Salud prepagada", 0.0)
            dep = st.checkbox('¿Tiene derecho a dependientes?')
            if dep and (sueldo_proporcional * 0.1) > (32 * uvt_2026):
                st.caption(f"⚠️ Tope 32 UVT aplicado: ${32*uvt_2026:,.0f}")

        with st.expander("🛡️ Rentas exentas (Art. 206 / 126 ET)"):
            fvp = st.number_input("Aportes FVP", 0.0)
            afc = st.number_input("Aportes AFC", 0.0)
            otras_ex = st.number_input("Otras rentas exentas", 0.0)
            detalle_ext, total_ext, div_usado = calcular_extras(sueldo_pactado, dict_extras, fecha_nomina)
        
        # --- NUEVA SECCIÓN INDEPENDIENTE ---
        st.subheader("📎 Otras Deducciones (Solo Salariales)")
        with st.expander("🚫 Terceros, Libranzas y Embargos"):
            libranzas = st.number_input("Libranzas", 0.0)
            embargos = st.number_input("Embargos (Alimentos/Cooperativas)", 0.0)
            cuotas_otros = st.number_input("Sindicatos/Otros", 0.0)

    if st.button("🚀 GENERAR REPORTE GERENCIAL", use_container_width=True):
        # 1. Cálculos Base
        v_ext, total_ext, div_usado = calcular_extras(sueldo_pactado, dict_extras, fecha_nomina)
        base_salarial = sueldo_proporcional + comisiones + total_ext + bono_pres
        ibc_ss = base_salarial * 0.7 if es_integral else base_salarial
        
        # 1. Obtenemos las deducciones fijas (Salud y Pensión)
        salud_e, pension_e = calcular_deducciones_ley(ibc_ss)
        
        # 2. CORRECCIÓN: Recibimos el VALOR y la TARIFA por separado
        # La función en formulas_nomina.py ya se encarga del tope de 25 SMMLV
        fsp, tasa_fsp_decimal = obtener_tarifa_fsp(ibc_ss)
        
        # 2. Retención
        ded_dict = {'medicina': med, 'vivienda': viv, 'dependientes': dep, 'pension_vol_obl': vol_obl}
        exe_dict = {'afc': afc, 'fvp': fvp, 'art206': {'otras': otras_ex}}
        base_uvt, base_grav_pesos = depurar_base_laboral(base_salarial, salud_e, pension_e, fsp, ded_dict, exe_dict)
        rete = calcular_retencion_final(base_uvt, metodo, pct_fijo)

        # 3. Costos y Totales
        aux_t = calcular_auxilio_transporte(sueldo_pactado) if (not es_integral and sueldo_pactado <= 2*smmlv_2026) else 0
        aux_t_prop = round((aux_t / 30) * (dias_lab - dias_aus), 0)
        total_devengado = base_salarial + bono_no_pres + aux_t_prop
        aplica_exo = exonerado_empresa and (min(ibc_ss, smmlv_2026*25) < (10 * smmlv_2026))
        prov = calcular_provisiones_mensuales(base_salarial, aux_t_prop, es_integral)
        para = calcular_parafiscales_y_ss(base_salarial, es_integral, aplica_exo)

        neto_final = total_devengado - salud_e - pension_e - fsp - rete
        costo_total_mes = total_devengado + sum(prov.values()) + sum(para.values())

        # --- SECCIÓN DE RESULTADOS Y ALERTAS ---
        st.markdown("---")
        if ibc_ss >= (smmlv_2026 * 25): st.warning(f"⚖️ IBC limitado a 25 SMMLV")
        if aplica_exo: st.success("✅ Exonerado Art. 114-1 ET")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Base UVT", f"{base_uvt}")
        m2.metric("Base Gravable", f"${base_grav_pesos:,.0f}")
        m3.metric("% FSP", f"{tasa_fsp_decimal*100:.1f}%")
        m4.metric("Rete Fuente", f"${rete:,.0f}")

        # --- 1. CÁLCULO DE TOTALES (Debe ir ANTES de cualquier tabla) ---
        total_devengado = (sueldo_proporcional + total_ext + aux_t_prop + 
                           comisiones + bono_pres + bono_no_pres)
        
        total_deducciones_ley = salud_e + pension_e + fsp + rete
        otras_deducciones_suma = libranzas + embargos + cuotas_otros
        
        # Totales finales para los subheadings
        neto_final = total_devengado - total_deducciones_ley - otras_deducciones_suma
        costo_total_mes = total_devengado + sum(prov.values()) + sum(para.values())

        # --- 2. CONSTRUCCIÓN DE DATAFRAMES ---
        df_em = pd.DataFrame([
            ("Devengos", None),
            ("Sueldo Proporcional.", sueldo_proporcional),
            ("Horas extras y recargos", total_ext),
            ("Auxilio de Transporte", aux_t_prop),
            ("Comisiones (Salarial)", comisiones),
            ("Bonificaciones Prestacionales", bono_pres),
            ("Pagos NO Prestacionales (Ley 1393)", bono_no_pres),
            ("Deducciones", None),
            ("Aporte Salud (4%)", -salud_e),
            ("Aporte Pensión (4%)", -pension_e),
            (f"Aporte FSP ({tasa_fsp_decimal*100:.1f}%)", -fsp),
            ("ReteFuente", -rete),
            ("Libranzas", -libranzas),
            ("Embargos", -embargos),
            ("Otras Cuotas", -cuotas_otros),
        ], columns=["Concepto", "Valor"])

        subtotal_ss = para.get('salud_patronal', 0) + para['pension_patronal'] + para.get('arl_1', 0)
        subtotal_paraf = para['caja_compensacion'] + para.get('sena', 0) + para.get('icbf', 0)

        df_pa = pd.DataFrame([
            ("Seguridad Social y ARL", None),
            ("Salud Patronal (8.5%)", para.get('salud_patronal', 0)),
            ("Pensión Patronal (12%)", para['pension_patronal']),
            (f"ARL ({nivel_arl})", para.get('arl_1', 0)),
            ("Provisión Pretacional", None), 
            ("Cesantías (8.33%)", prov.get('cesantias', 0)),
            ("Intereses sobre Cesantías (1%)", prov.get('intereses_cesantias', 0)),
            ("Prima de Servicios (8.33%)", prov.get('prima', 0)),
            ("Vacaciones (4.17%)", prov.get('vacaciones', 0)),
            ("Parafiscales", None),
            ("Caja de Compensación (4%)", para['caja_compensacion']),
            ("SENA (2%)", para.get('sena', 0)),
            ("ICBF (3%)", para.get('icbf', 0)),
        ], columns=["Concepto", "Valor"])

        
        st.subheader("📂 Exportar Auditoría")
        c_exp1, c_exp2, c_exp3 = st.columns(3)
        
        # CSV
        c_exp1.download_button("💾 CSV", pd.concat([df_em, df_pa]).to_csv(index=False).encode('utf-8'), "auditoria.csv", use_container_width=True)
        
        # EXCEL
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            df_em.to_excel(writer, sheet_name='Empleado', index=False)
            df_pa.to_excel(writer, sheet_name='Empresa', index=False)
        c_exp2.download_button("📊 Excel", buf.getvalue(), "auditoria.xlsx", use_container_width=True)

        # PDF
        pdf_bytes = generar_pdf_robusto(df_em, df_pa, neto_final, costo_total_mes, base_uvt)
        c_exp3.download_button("📄 PDF", pdf_bytes, "auditoria.pdf", use_container_width=True)

        # TABLAS VISUALES
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.write("**Desprendible Empleado**")
            st.table(df_em.style.format({"Valor": formato_contable}))
            st.subheader(f"NETO: ${neto_final:,.0f}")
            
        with col_res2:
            st.write("**Costo Empresa**")
            st.table(df_pa.style.format({"Valor": formato_contable}))
            st.subheader(f"TOTAL: ${costo_total_mes:,.0f}")
