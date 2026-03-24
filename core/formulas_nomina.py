def calcular_valor_hora(salario, horas_mes=210):
    return salario / horas_mes

def calcular_extras_detalladas(salario, extras_dict):
    v_h = calcular_valor_hora(salario)
    tarifas = {
        "hed": 1.25, "hen": 1.75, "heddf": 2.05, "hendf": 2.55,
        "rn": 1.35, "rdf": 1.80, "rndf": 2.15
    }
    totales = {k: round(v_h * tarifas[k] * extras_dict.get(k, 0), 0) for k in tarifas}
    return totales, sum(totales.values())

def calcular_deducciones_ley(ibc):
    # TOPE 25 SMMLV 2026
    smmlv = 1705905
    tope_25 = smmlv * 25
    ibc_final = min(ibc, tope_25)
    return round(ibc_final * 0.04, 0), round(ibc_final * 0.04, 0)

def obtener_tarifa_fsp(ibc):
    smmlv = 1705905
    # El FSP también se limita al IBC de 25 SMMLV
    ibc_limitado = min(ibc, smmlv * 25)
    if ibc_limitado < 4 * smmlv: return 0.0
    elif ibc_limitado < 16 * smmlv: return 0.01
    elif ibc_limitado < 17 * smmlv: return 0.012
    elif ibc_limitado < 18 * smmlv: return 0.014
    elif ibc_limitado < 19 * smmlv: return 0.016
    elif ibc_limitado < 20 * smmlv: return 0.018
    else: return 0.02

def calcular_fondo_solidaridad(ibc):
    smmlv = 1705905
    ibc_limitado = min(ibc, smmlv * 25)
    tarifa = obtener_tarifa_fsp(ibc_limitado)
    return round(ibc_limitado * tarifa, 0), tarifa
