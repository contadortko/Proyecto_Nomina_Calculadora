# src/core/motor_retencion.py
"""
MOTOR DE RETENCIÓN EN LA FUENTE — PROCEDIMIENTOS 1 Y 2
=======================================================
Implementa la depuración de la base gravable laboral y el cálculo
jurisdiccional de retención en la fuente.

Base Normativa Principal (Estatuto Tributario - ET):
- Art. 383, 386, 387, 388: Ley de retenciones laborales.
- Art. 55, 56: INCRGO (Ingresos no constitutivos de renta excluidos - Pension/Salud).
- Art. 126-1, 126-4: Aportes voluntarios a fondos de pensiones y cuentas AFC.
- Art. 206 (Rentas de trabajo exentas), numeral 10 modificado por Ley 2277.
- Art. 336 (Límite cedular del 40%, introducido Ley 2277 de 2022).

IMPORTANTE: Topes y límites se inyectan dinámicamente desde `parametros_dian.py`.
"""

from typing import Tuple, Dict

def depurar_base_laboral(
    ingreso_bruto: float,
    salud: float,
    pension: float,
    fsp: float,
    deducciones: Dict[str, float],
    exentas: Dict[str, float],
    uvt: float,
    topes_uvt: Dict[str, float]
) -> Tuple[float, float]:
    """
    Algoritmo contable para depurar la base gravable mensual.
    Flujo reglamentado por el Art. 388 del ET.

    Paso 1: Detraer INCRGO (Art. 55-56 ET)
    Paso 2: Sumar Deducciones Máximas (Art. 387 ET)
    Paso 3: Calcular Rentas Exentas (Arts. 126 y 206)
    Paso 4: Aplicar Tope Cedular del 40% (Art. 336 ET)
    """
    # ── PASO 1: Ingresos No Constitutivos de Renta (INCRGO) ──────────────────
    # Art. 55 y 56 ET: Seguridad Social y pensiones voluntarias al RAIS
    pension_vol_obl = deducciones.get("pension_vol_obl", 0.0)
    ingreso_neto = ingreso_bruto - (salud + pension + fsp + pension_vol_obl)

    # ── PASO 2: Deducciones permitidas (Art. 387 ET) ─────────────────────────
    # Intereses de crédito de vivienda (Art. 119 ET)
    tope_viv = topes_uvt.get("vivienda_mensual", 100.0) * uvt
    int_vivienda = min(deducciones.get("vivienda", 0.0), tope_viv)

    # Salud prepagada / seguros de salud (Art. 387 ET)
    tope_med = topes_uvt.get("medicina_prepagada_mensual", 16.0) * uvt
    prepago = min(deducciones.get("medicina", 0.0), tope_med)

    # Dependientes económicos (Art. 387 ET parágrafo 2) — 10% del bruto, máx 32 UVT
    tope_dep = topes_uvt.get("dependientes_mensual", 32.0) * uvt
    dep_val = min(ingreso_bruto * 0.10, tope_dep) if deducciones.get("dependientes") else 0.0

    total_deducciones = int_vivienda + prepago + dep_val

    # ── PASO 3: Rentas Exentas (Arts. 126-1, 126-4, 206 ET) ──────────────────
    # AFC + FVP: tope = mín(30% ingreso bruto, 3.800 UVT/año límite fraccionado mensual)
    tope_afc_mes = min(ingreso_bruto * 0.30, topes_uvt.get("afc_fvp_mensual", 316.6) * uvt)
    fvp_afc = min(deducciones.get("fvp", 0.0) + deducciones.get("afc", 0.0), tope_afc_mes)

    # Otras rentas exentas imputables (Art. 206 - Indemnizaciones, etc)
    art206 = exentas.get("art206", {})
    val_206 = sum(art206.values()) if isinstance(art206, dict) else 0.0

    # Renta exenta laboral 25% (Art. 206 Num.10 ET)
    base_para_25 = ingreso_neto - total_deducciones - fvp_afc - val_206
    renta_25 = base_para_25 * 0.25
    tope_25_mes = topes_uvt.get("renta_exenta_laboral_mensual", 65.8) * uvt
    renta_25 = min(renta_25, tope_25_mes)

    total_exentas = fvp_afc + val_206 + renta_25

    # ── PASO 4: Límite cedular del 40% (Art. 336 ET, Ley 2277/2022) ──────────
    beneficios_totales = total_deducciones + total_exentas
    limite_40_pct = ingreso_neto * 0.40
    limite_111_uvt = topes_uvt.get("limite_cedular_40_mensual", 111.6) * uvt

    beneficio_final = min(beneficios_totales, limite_40_pct, limite_111_uvt)

    # ── PASO 5: Base gravable ─────────────────────────────────────────────────
    base_gravable_pesos = max(ingreso_neto - beneficio_final, 0.0)
    base_uvt = base_gravable_pesos / uvt if uvt > 0.0 else 0.0

    return base_uvt, base_gravable_pesos


def calcular_retencion_final(base_uvt: float, uvt: float, procedimiento: int = 1, porcentaje_fijo: float = 0.0) -> int:
    """
    Calcula la retención en pesos aplicando la tabla de Ley y redondeos exigidos de la DIAN.

    Bases Legales:
    - Art. 383 ET: Tarifas escalonadas marginales para Procedimiento 1.
    - Art. 386 ET: Retención porcentual semestral del Procedimiento 2.
    - Art. 867 ET: Regla general de redondeo tributario al mil más cercano.
    """
    # Procedimiento 2 (Art. 386 ET)
    if procedimiento == 2:
        rete_cruda = (base_uvt * uvt) * (porcentaje_fijo / 100.0)
        return int(round(rete_cruda, -3))

    # ── Procedimiento 1: Tabla Progresiva Marginal (Art. 383 ET) ────────────
    UMBRAL_RETENCION_UVT = 95.0  # Umbral base exonerado

    if base_uvt <= UMBRAL_RETENCION_UVT:
        return 0

    # Lógica marginal matemática exacta a la transcripción legislativa DIAN
    if base_uvt <= 150.0:
        rete_uvt = (base_uvt - 95.0) * 0.19
    elif base_uvt <= 360.0:
        rete_uvt = (base_uvt - 150.0) * 0.28 + 10.0
    elif base_uvt <= 640.0:
        rete_uvt = (base_uvt - 360.0) * 0.33 + 69.0
    elif base_uvt <= 945.0:
        rete_uvt = (base_uvt - 640.0) * 0.35 + 162.0
    elif base_uvt <= 2300.0:
        rete_uvt = (base_uvt - 945.0) * 0.37 + 268.0
    else:
        rete_uvt = (base_uvt - 2300.0) * 0.39 + 770.0

    # Retorno en COP, redondeado al múltiplo de mil más cercano (Art. 867 ET)
    return int(round(rete_uvt * uvt, -3))
