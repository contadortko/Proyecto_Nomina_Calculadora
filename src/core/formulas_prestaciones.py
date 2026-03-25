# --- MOTOR DE PRESTACIONES Y PARAFISCALES AVANZADO 2026 ---

def calcular_auxilio_transporte(salario_base):
    smmlv_2026 = 1705905
    aux_trans_2026 = 249095
    return aux_trans_2026 if salario_base <= (smmlv_2026 * 2) else 0

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

def calcular_parafiscales_y_ss(base_salarial, es_integral, exonerado_114_1=True):
    # El IBC para integral es el 70% del salario total
    ibc_ss = base_salarial * 0.7 if es_integral else base_salarial
    return {
        "pension_patronal": ibc_ss * 0.12,
        "arl_1": ibc_ss * 0.00522,
        "caja_compensacion": ibc_ss * 0.04,
        "salud_patronal": 0 if exonerado_114_1 else ibc_ss * 0.085,
        "sena": 0 if exonerado_114_1 else ibc_ss * 0.02,
        "icbf": 0 if exonerado_114_1 else ibc_ss * 0.03
    }

# 1. Definir la Tabla de Cotización (Decreto 1765 de 2022)
TABLA_RIESGOS_ARL = {
    "Clase I (0.522%)": 0.00522,
    "Clase II (1.044%)": 0.01044,
    "Clase III (2.436%)": 0.02436,
    "Clase IV (4.350%)": 0.04350,
    "Clase V (6.960%)": 0.06960
}

def calcular_parafiscales_y_ss(base_salarial, es_integral, exonerado, clase_arl="Riesgo I (0.522%)"):
    """
    Cálculo de aportes patronales con nivel de riesgo variable y exoneración de impuestos.
    """
    # 1. Pension Patronal (12%)
    pension_pat = round(base_salarial * 0.12)
    
    # 2. Salud Patronal (8.5%) - Aplica exoneración si cumple requisitos
    # Si es exonerado y el salario < 10 SMMLV, es 0
    salud_pat = 0 if exonerado else round(base_salarial * 0.085)
    
    # 3. ARL - Según el nivel seleccionado
    tarifa_arl = TABLA_RIESGOS_ARL.get(clase_arl, 0.00522)
    arl_calculada = round(base_salarial * tarifa_arl)
    
    # 4. Parafiscales (Caja siempre se paga, SENA e ICBF pueden ser 0 por exoneración)
    caja = round(base_salarial * 0.04)
    sena_val = 0 if exonerado else round(base_salarial * 0.02)
    icbf_val = 0 if exonerado else round(base_salarial * 0.03)

    # --- EL PASO CRUCIAL: CONSTRUIR Y RETORNAR EL DICCIONARIO ---
    resultados = {
        "pension_patronal": pension_pat,
        "salud_patronal": salud_pat,
        "arl_1": arl_calculada,
        "caja_compensacion": caja,
        "sena": sena_val,
        "icbf": icbf_val
    }
    
    return resultados 