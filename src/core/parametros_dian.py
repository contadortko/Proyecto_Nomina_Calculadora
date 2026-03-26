# src/core/parametros_dian.py
"""
CEREBRO LEGAL ÚNICO — NOMINA INTELLIGENCE HUB
==============================================
Fuente centralizada de TODOS los parámetros normativos del sistema.
Ningun otro módulo debe definir constantes legales; solo importar de aquí.

Normas compiladas:
  - Decreto 1625 de 2016 (Único Reglamentario Tributario)
  - Estatuto Tributario Arts. 18, 114-1, 126-1/4, 206, 336, 383-388
  - Ley 2101 de 2021 (Reducción jornada laboral)
  - Ley 2466 de 2025 (Recargo dominical progresivo)
  - Decreto 1772 de 1994 (ARL)
  - Ley 100 de 1993 y sus reformas (Seguridad Social)
"""
from datetime import date
from typing import Dict, Any, Optional, List, Tuple


# ──────────────────────────────────────────────────────────────────────────────
# SECCIÓN 1: TABLAS LEGALES FIJAS (No dependen del año fiscal)
#
# Regulación normativa extraída integralmente de los códigos del Estado.
# ──────────────────────────────────────────────────────────────────────────────

# --- TARIFAS ARL (Clasificación de riesgo en el lugar de trabajo) ---
# Decreto 1772 de 1994, Art. 13 (Clases de Riesgo)
# Decreto 1765 de 2022 y Decreto 1072 de 2015 (Libro 2, Parte 2, Título 4)
# FUENTE ÚNICA: Importado y ejecutado por motor_costos_empresa.py
TARIFAS_ARL: Dict[str, float] = {
    "Riesgo I (0.522%)":  0.00522,   # Riesgo Mínimo (Oficinas, financieros, educativos)
    "Riesgo II (1.044%)": 0.01044,   # Riesgo Bajo (Manufactura textil, agro, sector ventas)
    "Riesgo III (2.436%)": 0.02436,  # Riesgo Medio (Manufactura industrial pesada, químicos)
    "Riesgo IV (4.350%)": 0.04350,   # Riesgo Alto (Transporte transporte, aceites, vidrios)
    "Riesgo V (6.960%)":  0.06960,   # Riesgo Máximo (Construcción, minería, explosivos, altos rangos)
}

# --- PORCENTAJES UNIVERSALES DE SEGURIDAD SOCIAL Y PARAFISCALES ---
# Base Jurídica:
# - Salud/Pensión: Art. 204 Ley 100 de 1993 y Art. 18 Ley 100 (tope de 25 SMMLV).
# - SENA: Ley 119 de 1994, Art. 30.
# - ICBF: Ley 27 de 1974 y Ley 89 de 1988.
# - Caja de Compensación: Ley 21 de 1982.
# Nota: La exoneración (SENA, ICBF, Salud empleador) bajo Art 114-1 ET se maneja en base al ingreso del empleado.
PORCENTAJES_SEGURIDAD_SOCIAL: Dict[str, float] = {
    "empleado_salud":     0.04,   # Aporte directo del trabajador (4%)
    "empleado_pension":   0.04,   # Aporte directo del trabajador (4%)
    "patronal_salud":     0.085,  # Carga de la empresa (8.5%)
    "patronal_pension":   0.12,   # Carga de la empresa (12%)
    "parafiscal_sena":    0.02,   # Servicio Nacional de Aprendizaje (2%)
    "parafiscal_icbf":    0.03,   # Bienestar Familiar (3%)
    "parafiscal_caja":    0.04,   # Caja de Compensación Familiar Obligatoria (4%)
}

# --- TOPES ANUALES Y MENSUALES DIAN EN UVT ---
# Completamente documentados con su artículo fuente.
# Los valores mensuales son = anual / 12 (redondeado al céntimo más cercano)
TOPES_TRIBUTARIOS_UVT: Dict[str, float] = {
    # ── Art. 383 ET: Umbral mínimo de retención mensual ──────────────────────
    "umbral_retencion_mensual":         95.0,   # Por debajo de 95 UVT/mes → retención 0%

    # ── Art. 387 ET: Deducciones de la base de retención ─────────────────────
    "vivienda_mensual":                100.0,   # Intereses crédito vivienda (Art.119 ET) — 100 UVT/mes
    "medicina_prepagada_mensual":       16.0,   # Salud prepagada / seguros salud — 16 UVT/mes
    "dependientes_mensual":             32.0,   # 10% ingresos brutos, máx 32 UVT/mes (Art.387)

    # ── Art. 126-1 / 126-4 ET: Aportes voluntarios AFC + FVP ─────────────────
    # Doble limitante: 30% del ingreso bruto Y máximo 3.800 UVT/año (≈316.67/mes)
    "afc_fvp_anual":                 3800.0,   # Tope anual absoluto Art.126-1/4
    "afc_fvp_mensual":              3800.0 / 12.0,  # Proxy mensual exacto

    # ── Art. 206 Num.10 ET (mod. Ley 2277/2022): Renta exenta laboral 25% ───
    # 25% del subtotal depurado; tope: 790 UVT/año (≈65.83/mes)
    "renta_exenta_laboral_anual":      790.0,  # Tope anual absoluto Art.206 Num.10
    "renta_exenta_laboral_mensual":     790.0 / 12.0, # Proxy mensual exacto

    # ── Art. 336 ET (Ley 2277/2022): Límite cedular 40% ─────────────────────
    # La SUMA de todas las deducciones + rentas exentas no puede superar:
    #   a) El 40% del ingreso neto, Y
    #   b) 1.340 UVT/año (≈111.67/mes)
    "limite_cedular_40_anual":        1340.0,  # Tope anual absoluto Art.336
    "limite_cedular_40_mensual":       1340.0 / 12.0, # Proxy mensual exacto

    # ── Art. 114-1 ET: Exoneración aportes patronales ────────────────────────
    # Sociedades exoneradas de SENA, ICBF y Salud patronal si empleado gana < 10 SMMLV
    "exoneracion_aportes_patronales_smmlv": 10.0,

    # ── Art. 18 Ley 100: Tope IBC Seguridad Social ───────────────────────────
    "tope_ibc_smmlv": 25.0,  # El IBC no puede superar 25 SMMLV
}

# --- ESCALAS FONDO DE SOLIDARIDAD PENSIONAL (FSP) ---
# Art. 2.2.14.1.6 Decreto 1833 de 2016.
# Estructura: (Límite_inferior_smmlv, Límite_superior_smmlv, Tarifa)
RANGOS_FSP: List[Tuple[float, float, float]] = [
    (4.0,  16.0, 0.010),   # De 4 a menos de 16 SMMLV → 1%
    (16.0, 17.0, 0.012),   # De 16 a 17 SMMLV → 1.2%
    (17.0, 18.0, 0.014),   # De 17 a 18 SMMLV → 1.4%
    (18.0, 19.0, 0.016),   # De 18 a 19 SMMLV → 1.6%
    (19.0, 20.0, 0.018),   # De 19 a 20 SMMLV → 1.8%
    (20.0, 999.0, 0.020),  # Más de 20 SMMLV → 2%
]


# ──────────────────────────────────────────────────────────────────────────────
# SECCIÓN 2: FUNCIONES DE PARÁMETROS FECHA-DEPENDIENTES
# ──────────────────────────────────────────────────────────────────────────────

def obtener_tabla_recargos(fecha_pago: date) -> Dict[str, float]:
    """
    Costos porcentuales unitarios y compuestos de recargos de ley.
    
    Bases Legales (CST Art. 168 y reformas transitorias):
    La progresividad del recargo dominical/festivo evoluciona en fases anuales.
    El factor base 1.0 asume que el recargo incluye la remuneración de la hora ordinaria dominical 
    (para el contexto de Trabajo Dominical Extraordinario).
    """
    recargos: Dict[str, float] = {
        "rn":  0.35,   # Recargo Nocturno (Solo recargo, no incluye base ordinaria)
        "hed": 1.25,   # Hora Extra Diurna (+25%)
        "hen": 1.75,   # Hora Extra Nocturna (+75%)
    }

    # Progresividad Recargo Dominical/Festivo — Aumento progresivo a 100%
    if fecha_pago >= date(2027, 7, 1):
        rdf_surcharge = 1.00   # 1 de julio de 2027: Sube al 100%
    elif fecha_pago >= date(2026, 7, 1):
        rdf_surcharge = 0.90   # 1 de julio de 2026: Sube al 90%
    elif fecha_pago >= date(2025, 7, 1):
        rdf_surcharge = 0.80   # 1 de julio de 2025: Sube al 80%
    else:
        rdf_surcharge = 0.75   # Histórico (Antes del 1 de julio 2025)

    # Factores integrados (incluyen la base 1.0 de pago más el recargo correspondiente)
    recargos["rdf"]   = 0.00 + rdf_surcharge
    recargos["heddf"] = 1.00 + rdf_surcharge + 0.25   # Extra Diurna D/F
    recargos["hendf"] = 1.00 + rdf_surcharge + 0.75   # Extra Nocturna D/F
    recargos["rndf"]  = 1.00 + rdf_surcharge + 0.35   # Recargo Nocturno D/F

    return recargos


def obtener_divisor_operativo(fecha_pago: date) -> int:
    """
    Divisor de horas para el cálculo del Valor Hora Ordinaria.
    
    Base Legal (Ley 2101 de 2021): 
    Reducción progresiva de la jornada laboral hasta 42 h/semana en julio de 2026.
    Fórmula contable: (Horas Secmanales / 6 días hábiles) * 30 días del mes.
    """
    if fecha_pago >= date(2026, 7, 15):
        return 210   # 42 h/semana -> 210 horas/mes
    elif fecha_pago >= date(2025, 7, 15):
        return 220   # 44 h/semana -> 220 horas/mes
    elif fecha_pago >= date(2024, 7, 15):
        return 230   # 46 h/semana -> 230 horas/mes
    elif fecha_pago >= date(2023, 7, 15):
        return 235   # 47 h/semana -> 235 horas/mes
    return 240       # 48 h/semana histórico -> 240 horas/mes


def obtener_alertas_legales(fecha_pago: date) -> List[str]:
    """Genera avisos críticos para el proceso de liquidación."""
    alertas = []

    # Jornada nocturna — Ley 2466/2025 (desde 26/dic/2025 inicia a las 19:00)
    if fecha_pago >= date(2025, 12, 26):
        alertas.append("⚠️ JORNADA NOCTURNA: Inicia a las 19:00hrs (Ley 2466/2025).")
    else:
        alertas.append("ℹ️ JORNADA NOCTURNA: Inicia a las 21:00hrs (Ley 1846/2017).")

    # Recargo dominical vigente
    recargo_actual = obtener_tabla_recargos(fecha_pago)["rdf"] * 100
    alertas.append(f"📢 RECARGO DOMINICAL: Liquidando al {recargo_actual:.0f}% (Ley 2466/2025).")

    # Jornada semanal — Ley 2101/2021
    if fecha_pago >= date(2026, 7, 15):
        alertas.append("✅ JORNADA LABORAL: 42h semanales — Divisor 210 (Ley 2101/2021).")
    else:
        dias_restantes = (date(2026, 7, 15) - date.today()).days
        if dias_restantes > 0:
            alertas.append(f"⚠️ Faltan {dias_restantes} días para la jornada de 42h (Ley 2101/2021).")
        else:
            alertas.append("✅ Jornada semanal reducida a 42h desde el 15/07/2026.")

    return alertas


# ──────────────────────────────────────────────────────────────────────────────
# SECCIÓN 3: HISTÓRICO DE VALORES LEGALES ANUALES (SMMLV / Aux. Transporte / UVT)
# ──────────────────────────────────────────────────────────────────────────────

HISTORICO_LEGAL: Dict[int, Dict[str, int]] = {
    1984: {"smmlv": 11298,    "aux_transporte": 0,       "uvt": 0},
    1985: {"smmlv": 13558,    "aux_transporte": 0,       "uvt": 0},
    1986: {"smmlv": 16811,    "aux_transporte": 0,       "uvt": 0},
    1987: {"smmlv": 20510,    "aux_transporte": 0,       "uvt": 0},
    1988: {"smmlv": 25637,    "aux_transporte": 0,       "uvt": 0},
    1989: {"smmlv": 32560,    "aux_transporte": 0,       "uvt": 0},
    1990: {"smmlv": 41025,    "aux_transporte": 5450,    "uvt": 0},
    1991: {"smmlv": 51716,    "aux_transporte": 6870,    "uvt": 0},
    1992: {"smmlv": 65190,    "aux_transporte": 8660,    "uvt": 0},
    1993: {"smmlv": 81510,    "aux_transporte": 10830,   "uvt": 0},
    1994: {"smmlv": 98700,    "aux_transporte": 13110,   "uvt": 0},
    1995: {"smmlv": 118933,   "aux_transporte": 15800,   "uvt": 0},
    1996: {"smmlv": 142125,   "aux_transporte": 18881,   "uvt": 0},
    1997: {"smmlv": 172005,   "aux_transporte": 22854,   "uvt": 0},
    1998: {"smmlv": 203826,   "aux_transporte": 27083,   "uvt": 0},
    1999: {"smmlv": 236460,   "aux_transporte": 31422,   "uvt": 0},
    2000: {"smmlv": 260100,   "aux_transporte": 34560,   "uvt": 0},
    2001: {"smmlv": 286000,   "aux_transporte": 38000,   "uvt": 0},
    2002: {"smmlv": 309000,   "aux_transporte": 41060,   "uvt": 0},
    2003: {"smmlv": 332000,   "aux_transporte": 44120,   "uvt": 0},
    2004: {"smmlv": 358000,   "aux_transporte": 47600,   "uvt": 0},
    2005: {"smmlv": 381500,   "aux_transporte": 50750,   "uvt": 0},
    2006: {"smmlv": 408000,   "aux_transporte": 47700,   "uvt": 20000},
    2007: {"smmlv": 433700,   "aux_transporte": 57700,   "uvt": 20974},
    2008: {"smmlv": 461500,   "aux_transporte": 61400,   "uvt": 22054},
    2009: {"smmlv": 496900,   "aux_transporte": 66100,   "uvt": 23763},
    2010: {"smmlv": 515000,   "aux_transporte": 68500,   "uvt": 24555},
    2011: {"smmlv": 535600,   "aux_transporte": 71200,   "uvt": 25132},
    2012: {"smmlv": 566700,   "aux_transporte": 75300,   "uvt": 26049},
    2013: {"smmlv": 589500,   "aux_transporte": 78350,   "uvt": 26841},
    2014: {"smmlv": 616000,   "aux_transporte": 81900,   "uvt": 27485},
    2015: {"smmlv": 644350,   "aux_transporte": 85600,   "uvt": 28279},
    2016: {"smmlv": 689455,   "aux_transporte": 91800,   "uvt": 29753},
    2017: {"smmlv": 737717,   "aux_transporte": 98200,   "uvt": 31859},
    2018: {"smmlv": 781242,   "aux_transporte": 104100,  "uvt": 33156},
    2019: {"smmlv": 828116,   "aux_transporte": 110400,  "uvt": 34270},
    2020: {"smmlv": 877803,   "aux_transporte": 102854,  "uvt": 35607},
    2021: {"smmlv": 908526,   "aux_transporte": 106454,  "uvt": 36308},
    2022: {"smmlv": 1000000,  "aux_transporte": 117172,  "uvt": 38004},
    2023: {"smmlv": 1160000,  "aux_transporte": 140606,  "uvt": 42412},
    2024: {"smmlv": 1300000,  "aux_transporte": 162000,  "uvt": 47065},
    2025: {"smmlv": 1423500,  "aux_transporte": 185000,  "uvt": 49799},
    2026: {"smmlv": 1705905,  "aux_transporte": 249095,  "uvt": 52374},  # Dec. 1469/2025 y 0159/2026; Res. DIAN 000238/2025
}


# ──────────────────────────────────────────────────────────────────────────────
# SECCIÓN 4: FUNCIÓN PRINCIPAL DE ACCESO A PARÁMETROS
# ──────────────────────────────────────────────────────────────────────────────

def obtener_constantes_nomina(fecha_pago: Optional[date] = None) -> Dict[str, Any]:
    """
    Retorna el diccionario completo de parámetros legales vigentes para la fecha dada.
    Es el punto de entrada único para todos los módulos del sistema.
    """
    if fecha_pago is None:
        fecha_pago = date.today()

    año = fecha_pago.year

    # Selección de vigencia: si el año no está en el histórico, usar el más cercano
    if año not in HISTORICO_LEGAL:
        año_ref = max(HISTORICO_LEGAL.keys()) if año > max(HISTORICO_LEGAL.keys()) else min(HISTORICO_LEGAL.keys())
        datos = HISTORICO_LEGAL[año_ref]
    else:
        datos = HISTORICO_LEGAL[año]

    return {
        # Valores base del año
        "smmlv":            datos["smmlv"],
        "aux_transporte":   datos["aux_transporte"],
        "uvt":              datos["uvt"],
        "año_ejecucion":    año,

        # Topes derivados del SMMLV
        "tope_25_smmlv":    datos["smmlv"] * 25,
        "tope_10_smmlv":    datos["smmlv"] * 10,   # Umbral exoneración Art.114-1

        # Tablas completas (única fuente de verdad)
        "porcentajes_ss":   PORCENTAJES_SEGURIDAD_SOCIAL,
        "topes_dian_uvt":   TOPES_TRIBUTARIOS_UVT,
        "tarifas_arl":      TARIFAS_ARL,

        # Información dinámica por fecha
        "recargos":         obtener_tabla_recargos(fecha_pago),
        "alertas":          obtener_alertas_legales(fecha_pago),
    }