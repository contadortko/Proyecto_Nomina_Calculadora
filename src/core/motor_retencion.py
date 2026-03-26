def obtener_tarifa_marginal(base_uvt):
    if base_uvt <= 95: return 0.0
    elif base_uvt <= 150: return 0.19
    elif base_uvt <= 360: return 0.28
    elif base_uvt <= 640: return 0.33
    elif base_uvt <= 945: return 0.35
    elif base_uvt <= 2300: return 0.37
    else: return 0.39

def depurar_base_laboral(ingreso_bruto, salud, pension, fsp, deducciones, exentas, uvt, topes_uvt):
    # 1. Ingresos No Constitutivos de Renta (I.N.C.R)
    pension_vol_obl = deducciones.get('pension_vol_obl', 0)
    ingreso_neto = ingreso_bruto - (salud + pension + fsp + pension_vol_obl)

    # 2. Deducciones (Art. 387 ET)
    # Intereses Vivienda
    int_viv = min(deducciones.get('vivienda', 0), topes_uvt["vivienda_mensual"] * uvt)
    
    # Salud Prepagada
    prepago = min(deducciones.get('medicina', 0), topes_uvt["medicina_prepagada_mensual"] * uvt)
    
    # Dependientes: 10% del bruto, tope legal dictado
    dep_val = (ingreso_bruto * 0.10) if deducciones.get('dependientes') else 0
    dep_val = min(dep_val, topes_uvt["dependientes_mensual"] * uvt)
    
    total_deducciones = int_viv + prepago + dep_val

    # 3. Rentas Exentas (Art. 206 y 126-1)
    # Aportes FVP/AFC: Tope 30% del ingreso, máximo dictado
    fvp_afc = deducciones.get('fvp', 0) + deducciones.get('afc', 0)
    fvp_afc = min(fvp_afc, ingreso_bruto * 0.30, topes_uvt["afc_fvp_mensual"] * uvt)
    
    # Otras rentas exentas (Indemnizaciones, etc - Art 206)
    art206 = exentas.get('art206', {})
    val_206 = sum(art206.values()) if isinstance(art206, dict) else 0
    
    # Renta Exenta Laboral (25%): Tope dictado
    base_para_25 = ingreso_neto - total_deducciones - fvp_afc - val_206
    renta_25 = (base_para_25 * 0.25)
    renta_25 = min(renta_25, topes_uvt["renta_exenta_laboral_mensual"] * uvt)
    
    total_exentas = fvp_afc + val_206 + renta_25

    # 4. Limitación del 40% (Art. 388 ET)
    beneficios_solicitados = total_deducciones + total_exentas
    max_40_pct = ingreso_neto * 0.40
    max_111_uvt = topes_uvt["limite_cedular_40_mensual"] * uvt
    
    beneficio_final = min(beneficios_solicitados, max_40_pct, max_111_uvt)
    
    base_gravable_pesos = ingreso_neto - beneficio_final
    base_uvt = round(base_gravable_pesos / uvt, 2)
    
    return base_uvt, base_gravable_pesos

def calcular_retencion_final(base_uvt, uvt, procedimiento=1, porcentaje_fijo=0):
    if procedimiento == 2:
        return round((base_uvt * uvt) * (porcentaje_fijo / 100), -3)
    
    # Procedimiento 1 - Tabla Art. 383
    if base_uvt <= 95: rete_uvt = 0
    elif base_uvt <= 150: rete_uvt = (base_uvt - 95) * 0.19
    elif base_uvt <= 360: rete_uvt = (base_uvt - 150) * 0.28 + 10
    elif base_uvt <= 640: rete_uvt = (base_uvt - 360) * 0.33 + 69
    elif base_uvt <= 945: rete_uvt = (base_uvt - 640) * 0.35 + 162
    elif base_uvt <= 2300: rete_uvt = (base_uvt - 945) * 0.37 + 268
    else: rete_uvt = (base_uvt - 2300) * 0.39 + 770
    
    return round(rete_uvt * uvt, -3) # Redondeo al mil más cercano (Art. 595)
