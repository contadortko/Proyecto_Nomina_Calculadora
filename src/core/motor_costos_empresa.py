# --- MOTOR DE PRESTACIONES Y PARAFISCALES AVANZADO 2026 ---

def calcular_auxilio_transporte(salario_base, smmlv, aux_transporte_oficial):
    return aux_transporte_oficial if salario_base <= (smmlv * 2) else 0

def calcular_provisiones_mensuales(base_salarial, aux_trans, es_integral, dias_trabajados=30):
    """
    Calcula provisiones usando la fórmula legal colombiana:
    (Base * Días) / 360
    """
    if es_integral:
        # Solo se provisiona vacaciones (Base * Días) / 720
        return {
            "prima": 0, 
            "cesantias": 0, 
            "intereses_cesantias": 0, 
            "vacaciones": round((base_salarial * dias_trabajados) / 720)
        }
    
    base_con_aux = base_salarial + aux_trans
    
    # 1. Prima de Servicios: (Base * Días) / 360
    prima = (base_con_aux * dias_trabajados) / 360
    
    # 2. Cesantías: (Base * Días) / 360
    cesantias = (base_con_aux * dias_trabajados) / 360
    
    # 3. Intereses sobre Cesantías: (Cesantías * Días * 0.12) / 360
    # Nota: El 0.12 es la tasa anual proporcional al tiempo laborado
    intereses = (cesantias * dias_trabajados * 0.12) / 360
    
    # 4. Vacaciones: (Base Salarial * Días) / 720
    # Se usa 720 porque son 15 días por año (360 / 15 = 24 meses -> 24 * 30 = 720)
    vacaciones = (base_salarial * dias_trabajados) / 720

    return {
        "prima": round(prima),
        "cesantias": round(cesantias),
        "intereses_cesantias": round(intereses),
        "vacaciones": round(vacaciones)
    }

# 1. Definir la Tabla de Cotización (Decreto 1765 de 2022)
TABLA_RIESGOS_ARL = {
    "Riesgo I (0.522%)": 0.00522,
    "Riesgo II (1.044%)": 0.01044,
    "Riesgo III (2.436%)": 0.02436,
    "Riesgo IV (4.350%)": 0.04350,
    "Riesgo V (6.960%)": 0.06960
}

def calcular_parafiscales_y_ss(base_salarial, es_integral, exonerado, porcentajes_ss, clase_arl="Riesgo I (0.522%)"):
    """
    Cálculo de aportes patronales con nivel de riesgo variable y exoneración de impuestos (Art. 114-1 E.T.).
    Integra reglas unificadas eliminando instancias redundantes.
    """
    # El IBC para integral es el 70% del salario total
    ibc_ss = base_salarial * 0.7 if es_integral else base_salarial
    
    # 1. Pension Patronal
    pension_pat = round(ibc_ss * porcentajes_ss["patronal_pension"])
    
    # 2. Salud Patronal - Aplica exoneración si cumple requisitos
    salud_pat = 0 if exonerado else round(ibc_ss * porcentajes_ss["patronal_salud"])
    
    # 3. ARL - Según el nivel seleccionado
    tarifa_arl = TABLA_RIESGOS_ARL.get(clase_arl, 0.00522)
    arl_calculada = round(ibc_ss * tarifa_arl)
    
    # 4. Parafiscales (Caja siempre se paga, SENA e ICBF pueden ser 0 por exoneración)
    caja = round(ibc_ss * porcentajes_ss["parafiscal_caja"])
    sena_val = 0 if exonerado else round(ibc_ss * porcentajes_ss["parafiscal_sena"])
    icbf_val = 0 if exonerado else round(ibc_ss * porcentajes_ss["parafiscal_icbf"])

    return {
        "pension_patronal": pension_pat,
        "salud_patronal": salud_pat,
        "arl_1": arl_calculada,
        "caja_compensacion": caja,
        "sena": sena_val,
        "icbf": icbf_val
    } 