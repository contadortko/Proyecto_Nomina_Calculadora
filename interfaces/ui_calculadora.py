import streamlit as st
import pandas as pd
import io
from fpdf import FPDF
from core.formulas_retencion import depurar_base_laboral, calcular_retencion_final
from core.formulas_prestaciones import calcular_auxilio_transporte, calcular_provisiones_mensuales, calcular_parafiscales_y_ss
from core.formulas_nomina import calcular_extras_detalladas, calcular_deducciones_ley, calcular_fondo_solidaridad

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
    st.title("🛡️ Auditoría de Nómina y Tributaria 2026")
    smmlv_2026 = 1705905
    uvt_2026 = 52374
    
    with st.sidebar:
        st.header("⚙️ Configuración Global")
        es_integral = st.toggle("Salario Integral")
        metodo = st.radio("Procedimiento Rete", [1, 2])
        pct_fijo = st.number_input("% Fijo (Proc 2)", 0.0) if metodo == 2 else 0.0
        exonerado_empresa = st.checkbox("Empresa Exonerada (Art. 114-1)", value=True)

    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("💰 Tiempo y Devengos")
        sueldo_pactado = st.number_input("Sueldo Mensual Full", value=1705905.0)
        col_d1, col_d2 = st.columns(2)
        dias_lab = col_d1.number_input("Días Laborados", 1, 30, value=30)
        dias_aus = col_d2.number_input("Días Ausencia/LNNR", 0, 30, value=0)
        sueldo_proporcional = round((sueldo_pactado / 30) * (dias_lab - dias_aus), 0)
        st.info(f"Liquidando sobre **{dias_lab - dias_aus}** días efectivos.")

        with st.expander("🕒 Horas Extras y Recargos (%)"):
            dict_extras = {
                "hed": st.number_input("Extra Diurno (1.25)", 0), "hen": st.number_input("Extra Nocturno (1.75)", 0),
                "heddf": st.number_input("Extra Diurno D/F (2.05)", 0), "hendf": st.number_input("Extra Nocturno D/F (2.55)", 0),
                "rn": st.number_input("Recargo Nocturno (0.35)", 0), "rdf": st.number_input("Recargo D/F (0.75)", 0),
                "rndf": st.number_input("Recargo Noct D/F (1.10)", 0)
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

    if st.button("🚀 GENERAR REPORTE GERENCIAL", use_container_width=True):
        # 1. Cálculos Base
        v_ext, total_ext = calcular_extras_detalladas(sueldo_pactado, dict_extras)
        base_salarial = sueldo_proporcional + comisiones + total_ext + bono_pres
        ibc_ss = base_salarial * 0.7 if es_integral else base_salarial
        salud_e, pension_e = calcular_deducciones_ley(ibc_ss)
        fsp, tarifa_fsp = calcular_fondo_solidaridad(base_salarial)
        
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
        m3.metric("% FSP", f"{tarifa_fsp*100:.1f}%")
        m4.metric("Rete Fuente", f"${rete:,.0f}")

        # --- EXPORTACIÓN ---
        df_em = pd.DataFrame([
            ("Sueldo Prop.", sueldo_proporcional), ("Extras", total_ext), ("Aux. Transp.", aux_t_prop),
            ("Bonos/Comis.", comisiones+bono_pres+bono_no_pres), ("Deducciones Ley", -(salud_e+pension_e+fsp)), ("ReteFuente", -rete)
        ], columns=["Concepto", "Valor"])

        df_pa = pd.DataFrame([
            ("Provisiones", sum(prov.values())), ("Pensión Pat.", para['pension_patronal']), 
            ("ARL/Caja", para['arl_1']+para['caja_compensacion']), ("Salud/SENA/ICBF Pat.", para.get('salud_patronal',0)+para.get('sena',0)+para.get('icbf',0))
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
            st.table(df_em.style.format({"Valor": "${:,.0f}"}))
            st.subheader(f"NETO: ${neto_final:,.0f}")
        with col_res2:
            st.write("**Costo Empresa**")
            st.table(df_pa.style.format({"Valor": "${:,.0f}"}))
            st.subheader(f"TOTAL: ${costo_total_mes:,.0f}")
