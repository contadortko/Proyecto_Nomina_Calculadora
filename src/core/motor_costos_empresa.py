# src/core/motor_costos_empresa.py
"""
MOTOR DE PRESTACIONES Y PARAFISCALES — COSTO REAL EMPRESA
==========================================================
Calcula provisiones de prestaciones sociales y aportes institucionales patronales.

Base Normativa Principal:
- Código Sustantivo del Trabajo (CST)
- Ley 100 de 1993 (Seguridad Social)
- Estatuto Tributario (ET)

IMPORTANTE: TARIFAS_ARL se importa desde parametros_dian.py (fuente única).
"""
from typing import Dict
from src.core.parametros_dian import TARIFAS_ARL


def calcular_auxilio_transporte(salario_base: float, smmlv: float, aux_transporte_oficial: float) -> float:
    """
    Evalúa la procedencia del auxilio de transporte.
    
    Base Legal:
    - Ley 15 de 1959 y CST Art. 2: Aplica solo si el salario <= 2 SMMLV.
    """
    return aux_transporte_oficial if salario_base <= (smmlv * 2.0) else 0.0


def calcular_provisiones_mensuales(base_salarial: float, aux_trans: float, es_integral: bool, dias_trabajados: int = 30) -> Dict[str, int]:
    """
    Provisiones mensuales proyectadas de prestaciones sociales laborales.

    Bases Legales (Código Sustantivo del Trabajo - CST):
    - Prima de Servicios: CST Art. 306.
    - Cesantías: CST Art. 249.
    - Intereses sobre Cesantías: Ley 52 de 1975, Art. 1 (12% anual).
    - Vacaciones: CST Art. 186 (15 días de salario por año lab., sin incluir auxilio de transporte).
    - Salario integral: CST Art. 132 (Factor prestacional absorbido > 10 SMMLV).

    El divisor estándar contable es 360 (días/año), para vacaciones es 720 (por ser 15 días anuales).
    """
    if es_integral:
        # El 30% del salario integral ya suple las prestaciones, a excepción de las vacaciones.
        return {
            "prima":                 0,
            "cesantias":             0,
            "intereses_cesantias":   0,
            "vacaciones":            round((base_salarial * dias_trabajados) / 720),
        }

    base_con_aux = base_salarial + aux_trans

    return {
        "prima":                round((base_con_aux * dias_trabajados) / 360),
        "cesantias":            round((base_con_aux * dias_trabajados) / 360),
        "intereses_cesantias":  round(((base_con_aux * dias_trabajados) / 360) * 0.12),
        "vacaciones":           round((base_salarial * dias_trabajados) / 720),
    }


def calcular_parafiscales_y_ss(
    base_salarial: float,
    es_integral: bool,
    exonerado: bool,
    porcentajes_ss: dict,
    clase_arl: str = "Riesgo I (0.522%)"
) -> Dict[str, int]:
    """
    Cálculo de Aportes Patronales a Seguridad Social y Sistemas Parafiscales.

    Bases Legales:
    - Art. 114-1 ET: Exoneración patronal a SENA, ICBF y Salud (para ingresos <10 SMMLV).
    - Art. 49 Ley 789/2002: IBC del Salario Integral corresponde al 70%.
    - Ley 119/1994 Art. 30 (SENA) y Ley 27/1974 (ICBF).
    - Decreto 1772 de 1994: Clasificación del Riesgo de ARL.

    Args:
        base_salarial: Bruto sin auxilio de transporte.
        es_integral: True si el contrato pactó salario integral.
        exonerado: Dictamen previo de exoneración (Art 114-1).
        clase_arl: String clasificador según TARIFAS_ARL.
    """
    # Determinación de IBC base (Art. 49 Ley 789/2002)
    ibc_ss = base_salarial * 0.7 if es_integral else base_salarial

    # Aportes incondicionales (Siempre se liquidan)
    pension_pat = round(ibc_ss * porcentajes_ss.get("patronal_pension", 0.12))
    caja        = round(ibc_ss * porcentajes_ss.get("parafiscal_caja", 0.04))
    
    tarifa_arl = TARIFAS_ARL.get(clase_arl, 0.00522)
    arl_1      = round(ibc_ss * tarifa_arl)

    # Aportes condicionados a Exoneración (Art. 114-1 ET)
    salud_pat = 0 if exonerado else round(ibc_ss * porcentajes_ss.get("patronal_salud", 0.085))
    sena      = 0 if exonerado else round(ibc_ss * porcentajes_ss.get("parafiscal_sena", 0.02))
    icbf      = 0 if exonerado else round(ibc_ss * porcentajes_ss.get("parafiscal_icbf", 0.03))

    return {
        "pension_patronal":   pension_pat,
        "salud_patronal":     salud_pat,
        "arl_1":              arl_1,
        "caja_compensacion":  caja,
        "sena":               sena,
        "icbf":               icbf,
    }