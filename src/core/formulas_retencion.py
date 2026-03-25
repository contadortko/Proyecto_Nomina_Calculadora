def obtener_tarifa_marginal(base_uvt):
    if base_uvt <= 95: return 0.0
    elif base_uvt <= 150: return 0.19
    elif base_uvt <= 360: return 0.28
    elif base_uvt <= 640: return 0.33
    elif base_uvt <= 945: return 0.35
    elif base_uvt <= 2300: return 0.37
    else: return 0.39

def depurar_base_laboral(ingreso_bruto, salud, pension, fsp, deducciones, exentas):
    uvt_2026 = 52374
    
    # 1. Ingresos No Constitutivos de Renta (I.N.C.R)
    # Incluye Salud, Pensión, FSP y el nuevo campo de Pensión Voluntaria (Art. 55)
    pension_vol_obl = deducciones.get('pension_vol_obl', 0)
    # Límite Art. 55: Los aportes al RAIS no tienen un tope mensual específico como deducción, 
    # sino que se restan directamente del bruto.
    ingreso_neto = ingreso_bruto - (salud + pension + fsp + pension_vol_obl)

    # 2. Deducciones (Art. 387 ET)
    # Intereses Vivienda: Tope 100 UVT mes
    int_viv = min(deducciones.get('vivienda', 0), 100 * uvt_2026)
    
    # Salud Prepagada: Tope 16 UVT mes
    prepago = min(deducciones.get('medicina', 0), 16 * uvt_2026)
    
    # Dependientes: 10% del bruto, tope 32 UVT mes
    dep_val = (ingreso_bruto * 0.10) if deducciones.get('dependientes') else 0
    dep_val = min(dep_val, 32 * uvt_2026)
    
    total_deducciones = int_viv + prepago + dep_val

    # 3. Rentas Exentas (Art. 206 y 126-1)
    # Aportes FVP/AFC: Tope 30% del ingreso, máximo 3.800 UVT año (316.6 UVT mes)
    fvp_afc = deducciones.get('fvp', 0) + deducciones.get('afc', 0)
    fvp_afc = min(fvp_afc, ingreso_bruto * 0.30, 316.6 * uvt_2026)
    
    # Otras rentas exentas (Indemnizaciones, etc - Art 206)
    art206 = exentas.get('art206', {})
    val_206 = sum(art206.values()) if isinstance(art206, dict) else 0
    
    # Renta Exenta Laboral (25%): Tope 65.8 UVT mes
    base_para_25 = ingreso_neto - total_deducciones - fvp_afc - val_206
    renta_25 = (base_para_25 * 0.25)
    renta_25 = min(renta_25, 65.8 * uvt_2026)
    
    total_exentas = fvp_afc + val_206 + renta_25

    # 4. Limitación del 40% (Art. 388 ET)
    # La suma de deducciones y exentas no puede superar el 40% del ingreso neto
    # ni el tope mensual de 111.67 UVT
    beneficios_solicitados = total_deducciones + total_exentas
    max_40_pct = ingreso_neto * 0.40
    max_111_uvt = 111.67 * uvt_2026
    
    beneficio_final = min(beneficios_solicitados, max_40_pct, max_111_uvt)
    
    base_gravable_pesos = ingreso_neto - beneficio_final
    base_uvt = round(base_gravable_pesos / uvt_2026, 2)
    
    return base_uvt, base_gravable_pesos

def calcular_retencion_final(base_uvt, procedimiento=1, porcentaje_fijo=0):
    uvt_2026 = 52374
    if procedimiento == 2:
        return round((base_uvt * uvt_2026) * (porcentaje_fijo / 100), -3)
    
    # Procedimiento 1 - Tabla Art. 383
    if base_uvt <= 95: rete_uvt = 0
    elif base_uvt <= 150: rete_uvt = (base_uvt - 95) * 0.19
    elif base_uvt <= 360: rete_uvt = (base_uvt - 150) * 0.28 + 10
    elif base_uvt <= 640: rete_uvt = (base_uvt - 360) * 0.33 + 69
    elif base_uvt <= 945: rete_uvt = (base_uvt - 640) * 0.35 + 162
    elif base_uvt <= 2300: rete_uvt = (base_uvt - 945) * 0.37 + 268
    else: rete_uvt = (base_uvt - 2300) * 0.39 + 770
    
    return round(rete_uvt * uvt_2026, -3) # Redondeo al mil más cercano (Art. 595)
