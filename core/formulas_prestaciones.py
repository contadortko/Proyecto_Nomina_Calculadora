# --- MOTOR DE PRESTACIONES Y PARAFISCALES AVANZADO 2026 ---

def calcular_auxilio_transporte(salario_base):
    smmlv_2026 = 1705905
    aux_trans_2026 = 249095
    return aux_trans_2026 if salario_base <= (smmlv_2026 * 2) else 0

def calcular_provisiones_mensuales(base_salarial, aux_trans, es_integral):
    if es_integral:
        # En integral, prima y cesantías están en el 30% prestacional. Solo se provisiona vacaciones.
        return {"prima": 0, "cesantias": 0, "int_cesantias": 0, "vacaciones": base_salarial * 0.0417}
    
    base_con_aux = base_salarial + aux_trans
    return {
        "prima": base_con_aux * 0.0833,
        "cesantias": base_con_aux * 0.0833,
        "int_cesantias": (base_con_aux * 0.0833) * 0.12,
        "vacaciones": base_salarial * 0.0417
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
