# src/core/motor_devengos.py
"""
MOTOR DE DEVENGOS Y DEDUCCIONES DE LEY
=======================================
Calcula extras, recargos, aportes obligatorios a SS y FSP.

Base Normativa Principal:
- Código Sustantivo del Trabajo (CST): Arts. 160, 161, 168 (Jornada y recargos)
- Ley 100 de 1993 y Ley 797 de 2003 (Sistema General de Seguridad Social)

IMPORTANTE: Este módulo NO define constantes legales propias.
Todas las tablas se importan desde parametros_dian.py (fuente única).
"""
from datetime import date
from typing import Dict, Tuple

# Importamos las funciones centralizadas — NO se duplica lógica aquí
from src.core.parametros_dian import (
    obtener_tabla_recargos,
    obtener_divisor_operativo,
    RANGOS_FSP,
)


def calcular_extras(salario: float, novedades: dict, fecha_nomina: date) -> Tuple[Dict[str, float], float, int]:
    """
    Calcula el valor de cada tipo de hora extra y recargo.
    
    Bases legales:
    - CST Art. 168: Recargos y trabajo suplementario.
    - Ley 2466 de 2025: Progresividad del recargo dominical y nocturno.
    - Ley 2101 de 2021: Reducción de la jornada laboral (divisor base).

    Args:
        salario: Salario base mensual pactado.
        novedades: Dict con cantidades de horas por tipo (ej. {'hed': 2, 'rn': 5}).
        fecha_nomina: Fecha para inyectar correctamente la progresividad legal.

    Returns:
        (detalle_valores, total_pesos, divisor_usado)
    """
    divisor = obtener_divisor_operativo(fecha_nomina)
    recargos = obtener_tabla_recargos(fecha_nomina)
    valor_hora = salario / divisor

    # Optimización: Comprensión de diccionario iterando solo sobre novedades reportadas
    detalle = {
        clave: round(valor_hora * recargos[clave] * horas)
        for clave, horas in novedades.items()
        if horas > 0 and clave in recargos
    }

    return detalle, sum(detalle.values()), divisor


def calcular_deducciones_ley(ibc: float, smmlv: float, porcentajes_ss: dict) -> Tuple[int, int]:
    """
    Aportes obligatorios a Seguridad Social del empleado (Salud y Pensión).
    
    Bases legales:
    - Art. 204, Ley 100 de 1993 (Tarifas SS).
    - Art. 18, Ley 100 de 1993 (Tope máximo IBC de 25 SMMLV).

    Returns:
        (salud_empleado, pension_empleado) en pesos (redondeados al entero).
    """
    # Límite superior de cotización: 25 SMMLV
    ibc_limitado = min(ibc, smmlv * 25.0)
    
    salud = round(ibc_limitado * porcentajes_ss.get("empleado_salud", 0.04))
    pension = round(ibc_limitado * porcentajes_ss.get("empleado_pension", 0.04))
    
    return salud, pension


def obtener_tarifa_fsp(ibc: float, smmlv: float) -> Tuple[int, float]:
    """
    Determina el aporte al Fondo de Solidaridad Pensional (FSP).
    
    Bases legales:
    - Art. 27, Ley 100 de 1993 modificado por Art. 2, Ley 797 de 2003.
    - Art. 2.2.14.1.6 Decreto 1833 de 2016 (Rangos y tarifas Subsistencia).
    
    Condiciones de Ley:
    Solo aplica si el IBC es mayor o igual a 4 SMMLV. Tope de cotización en 25 SMMLV.

    Returns:
        (valor_fsp_pesos, tarifa_decimal_aplicada)
    """
    # Límite superior de cotización aplicable al FSP (25 SMMLV)
    ibc_limitado = min(ibc, smmlv * 25.0)
    n_smmlv = ibc_limitado / smmlv

    # Excepción por límite inferior legal
    if n_smmlv < 4.0:
        return 0, 0.0

    tarifa = 0.020  # Por defecto tarifa máxima legal (>20 SMMLV)
    
    # Evalúa la matriz progresiva de solidaridad y subsistencia
    for limite_inf, limite_sup, t in RANGOS_FSP:
        if limite_inf <= n_smmlv < limite_sup:
            tarifa = t
            break  # Algoritmo eficiente, detiene búsqueda al hallar rango

    valor_fsp = round(ibc_limitado * tarifa)
    return valor_fsp, tarifa