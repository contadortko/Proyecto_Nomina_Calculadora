# src/core/base_legal.py
# Permite el manejo y comparación de fechas (vital para cambios de ley como la reducción de jornada)
from datetime import date

# Habilita el 'Type Hinting', que documenta y asegura que las funciones reciban y entreguen 
# los datos correctos (Diccionarios, Listas, Tuplas), evitando errores contables en la ejecución.
from typing import Dict, Any, Optional, List, Tuple


"""
MÓDULO DE PARÁMETROS PARA LIQUIDACIÓN DE NÓMINA - SISTEMA DE GESTIÓN
-----------------------------------------------------------------------
Este módulo centraliza los valores vigentes para el procesamiento de 
pagos, aportes y deducciones de nómina en Colombia.
"""

# --- HISTÓRICO DE HORAS EXTRAS Y RECARGOS (Evolutivo por Ley 2466 de 2025) ---
def obtener_tabla_recargos(fecha_pago: date) -> Dict[str, float]:
    """
    Calcula los porcentajes de recargos vigentes según la escala de 
    progresividad de la Ley 2466 del 25 de junio de 2025.
    """
    # 1. Factores base que se mantienen constantes
    recargos = {
        "rn": 0.35,     # Recargo Nocturno (35%)
        "hed": 1.25,    # Hora Extra Diurna (Factor 1.25)
        "hen": 1.75,    # Hora Extra Nocturna (Factor 1.75)
    }

    # 2. Lógica de PROGRESIVIDAD para Recargo Dominical y Festivo (DDO)
    # Basado en la tabla de la Ley 2466 de 2025
    if fecha_pago >= date(2027, 7, 1):
        recargos["rdf"] = 1.00  # Meta final: 100% Recargo Dominical
    elif fecha_pago >= date(2026, 7, 1):
        recargos["rdf"] = 0.90  # Transición: 90% Recargo Dominical
    elif fecha_pago >= date(2025, 7, 1):
        recargos["rdf"] = 0.80  # Inicio: 80% Recargo Dominical
    else:
        recargos["rdf"] = 0.75  # Estándar histórico (75%)

    # 3. Cálculo de factores compuestos para horas extras en dominicales
    # Se suma el 1.00 de la hora ordinaria + el recargo correspondiente
    recargos["heddf"] = 1.00 + recargos["rdf"] + 0.25 # Extra Diurna Dom (Factor 2.0 en 2027)
    recargos["hendf"] = 1.00 + recargos["rdf"] + 0.75 # Extra Nocturna Dom (Factor 2.5 en 2027)
    recargos["rndf"] = recargos["rn"] + recargos["rdf"] # Recargo Nocturno Dom (Factor 1.35 en 2027)
    
    return recargos

def obtener_alertas_legales(fecha_pago: date) -> List[str]:
    """Genera avisos críticos para el proceso de liquidación de nómina."""
    alertas = []
    
    # 1. Hito Ley 2466/2025 - Cambio de inicio Jornada Nocturna
    # La ley establece el cambio a partir del 26 de diciembre de 2025
    FECHA_CAMBIO_NOCTURNA = date(2025, 12, 26)
    if fecha_pago >= FECHA_CAMBIO_NOCTURNA:
        alertas.append("⚠️ JORNADA NOCTURNA: Inicia a las 19:00hrs y termina a las 06:00hrs (Ley 2466/2025).")
    else:
        alertas.append("ℹ️ JORNADA NOCTURNA: Inicia a las 21:00hrs y termina a las 06:00hrs (Ley 1846/2017).")
    
    # Notificación de Progresividad Dominical (Ley 2466)
    recargo_actual = obtener_tabla_recargos(fecha_pago)["rdf"] * 100
    alertas.append(f"📢 RECARGO DOMINICAL: Liquidando al {recargo_actual:.0f}% (Ley 2466/2025).")
    
    # Notificación de Jornada Semanal (Ley 2101)
    if fecha_pago >= date(2026, 7, 15):
        alertas.append("✅ JORNADA LABORAL: 42h semanales (Divisor 210 horas/mes) (Ley Ley 2101/2021).")
    else:
        alertas.append("ℹ️ JORNADA LABORAL: 44h semanales (Divisor 220 horas/mes) (Ley Ley 2101/2021).")
        
    
    
    #Contador y Notificación de la disminución de la Jornada Laboral a 42h (Ley 2101/2021)
    fecha_hito_42h = date(2026, 7, 15)
    fecha_actual = date.today()
    if fecha_actual < fecha_hito_42h:
        dias_faltantes = (fecha_hito_42h - fecha_actual).days
        alertas.append(f"⚠️ **Alerta Legal:** Faltan {dias_faltantes} días para el cambio a 42h (Ley 2101/2021).")
    else:
        alertas.append("✅ **Jornada semanal reducida a 42h desde el 15/07/2026.")
    
    return alertas

# --- TABLA DE TARIFAS ARL (Decreto 1772 de 1994) ---
# Niveles de riesgo para el cálculo de aportes patronales.
TARIFAS_ARL: Dict[int, float] = {
    1: 0.00522,     # Riesgo I - Mínimo
    2: 0.01044,     # Riesgo II - Bajo
    3: 0.02436,     # Riesgo III - Medio
    4: 0.04350,     # Riesgo IV - Alto
    5: 0.06700      # Riesgo V - Máximo
}


# --- ESCALAS FONDO DE SOLIDARIDAD PENSIONAL (FSP) ---
# Basado en el número de SMMLV del IBC (Art. 2.2.14.1.6 Dec. 1833 de 2016).
# Estructura: (Límite Inferior, Límite Superior, Tarifa)
RANGOS_FSP: List[Tuple[float, float, float]] = [
    (4.0, 16.0, 0.010),   # De 4 a menos de 16 SMMLV
    (16.0, 17.0, 0.012),  # De 16 a 17 SMMLV
    (17.0, 18.0, 0.014),  # De 17 a 18 SMMLV
    (18.0, 19.0, 0.016),  # De 18 a 19 SMMLV
    (19.0, 20.0, 0.018),  # De 19 a 20 SMMLV
    (20.0, 999.0, 0.020)  # Más de 20 SMMLV
]




# --- PARÁMETROS DE LIQUIDACIÓN ANUAL ---
# Valores maestros para la ejecución de la nómina.
HISTORICO_LEGAL: Dict[int, Dict[str, int]] = {
    
    1984: {
        "smmlv": 11298,         # Normativa Decreto 3506 de diciembre de 1983
        "aux_transporte": 0, 
        "uvt": 0
    },  
    1985: {
        "smmlv": 13558,         # Normativa Decreto 1 de enero de 1985
        "aux_transporte": 0, 
        "uvt": 0
    },  
    1986: {
        "smmlv": 16811,         # Normativa Decreto 3754 de diciembre de 1985
        "aux_transporte": 0, 
        "uvt": 0
    },  
    1987: {
        "smmlv": 20510,         # Normativa Decreto 3732 de diciembre de 1986
        "aux_transporte": 0, 
        "uvt": 0
    },  
    1988: {
        "smmlv": 25637,         # Normativa Decreto 2545 de diciembre de 1987
        "aux_transporte": 0, 
        "uvt": 0
    },  
    1989: {
        "smmlv": 32560,         # Normativa Decreto 2662 de diciembre de 1988
        "aux_transporte": 0, 
        "uvt": 0
    },  
    1990: {
        "smmlv": 41025,         # Normativa Decreto 3000 de diciembre de 1989
        "aux_transporte": 5450, 
        "uvt": 0
    },
    1991: {
        "smmlv": 51716,         # Normativa Decreto 3074 de diciembre de 1990
        "aux_transporte": 6870, 
        "uvt": 0
    },  
    1992: {
        "smmlv": 65190,         # Normativa Decreto 2867 de diciembre de 1991
        "aux_transporte": 8660, 
        "uvt": 0
    },  
    1993: {
        "smmlv": 81510,         # Normativa Decreto 2061 de diciembre de 1992
        "aux_transporte": 10830, 
        "uvt": 0
    }, 
    1994: {
        "smmlv": 98700,         # Normativa Decreto 2548 de diciembre de 1993
        "aux_transporte": 13110, 
        "uvt": 0
    }, 
    1995: {
        "smmlv": 118933,        # Normativa Decreto 2872 de diciembre de 1994
        "aux_transporte": 15800, 
        "uvt": 0
    },
    1996: {
        "smmlv": 142125,        # Normativa Decreto 2310 de diciembre de 1995
        "aux_transporte": 18881, 
        "uvt": 0
    },
    1997: {
        "smmlv": 172005,        # Normativa Decreto 2334 de diciembre de 1996
        "aux_transporte": 22854, 
        "uvt": 0
    },
    1998: {
        "smmlv": 203826,        # Normativa Decreto 3106 de diciembre de 1997
        "aux_transporte": 27083, 
        "uvt": 0
    },
    1999: {
        "smmlv": 236460,        # Normativa Decreto 2560 de diciembre de 1998
        "aux_transporte": 31422, 
        "uvt": 0
    },
    2000: {
        "smmlv": 260100,        # Normativa Decreto 2647 de dic 23 de 1999
        "aux_transporte": 34560, 
        "uvt": 0
    },
    2001: {
        "smmlv": 286000,        # Normativa Decreto 2579 de dic 13 de 2000
        "aux_transporte": 38000, 
        "uvt": 0
    },
    2002: {
        "smmlv": 309000,        # Normativa Decreto 2910 de dic 31 de 2001
        "aux_transporte": 41060, 
        "uvt": 0
    },
    2003: {
        "smmlv": 332000,        # Normativa Decreto 3232 de dic 27 de 2002
        "aux_transporte": 44120, 
        "uvt": 0
    },
    2004: {
        "smmlv": 358000,        # Normativa Decreto 3770 de dic 26 de 2003
        "aux_transporte": 47600, 
        "uvt": 0
    },
    2005: {
        "smmlv": 381500,        # Normativa Decreto 4360 de dic 22 de 2004
        "aux_transporte": 50750, 
        "uvt": 0
    },
    2006: {
        "smmlv": 408000,        # Normativa Decreto 4686 de dic 21 de 2005
        "aux_transporte": 47700, 
        "uvt": 20000            # Ley 1116 de 2006
    }, 
    2007: {
        "smmlv": 433700,        # Normativa Decreto 4580 de dic 27 de 2006
        "aux_transporte": 57700, 
        "uvt": 20974            # Resolución DIAN número 15652 de 2006
    }, 
    2008: {
        "smmlv": 461500,        # Normativa Decreto 4965 de dic 27 de 2007
        "aux_transporte": 61400, 
        "uvt": 22054            # Resolución DIAN número 15013 de 2007
    }, 
    2009: {
        "smmlv": 496900,        # Normativa Decreto 4868 de dic 30 de 2008
        "aux_transporte": 66100, 
        "uvt": 23763            # Resolución DIAN número 01063 de 2008
    }, 
    2010: {
        "smmlv": 515000,        # Normativa Decreto 5053 de dic 30 de 2009
        "aux_transporte": 68500, 
        "uvt": 24555            # Resolución DIAN número 012115 de 2009
    }, 
    2011: {
        "smmlv": 535600,        # Normativa Decreto 033 de enero 11 de 2011
        "aux_transporte": 71200, 
        "uvt": 25132            # Resolución DIAN número 012066 de 2010
    }, 
    2012: {
        "smmlv": 566700,        # Normativa Decreto 4919 de dic 26 de 2011
        "aux_transporte": 75300, 
        "uvt": 26049            # Resolución DIAN número 011963 de 2011
    }, 
    2013: {
        "smmlv": 589500,        # Normativa Decreto 2738 de dic 28 de 2012
        "aux_transporte": 78350, 
        "uvt": 26841            # Resolución DIAN número 00138 de 2012
    }, 
    2014: {
        "smmlv": 616000,        # Normativa Decreto 3068 de dic 30 de 2013
        "aux_transporte": 81900, 
        "uvt": 27485            # Resolución DIAN número 000227 de 2013
    }, 
    2015: {
        "smmlv": 644350,        # Normativa Decreto 2731 de dic 30 de 2014
        "aux_transporte": 85600, 
        "uvt": 28279            # Resolución DIAN número 000245 de 2014
    },
    2016: {
        "smmlv": 689455,        # Normativa Decreto 2552 de dic 30 de 2015
        "aux_transporte": 91800, 
        "uvt": 29753            # Resolución DIAN número 000115 dic 2015
    }, 
    2017: {
        "smmlv": 737717,        # Normativa Decreto 2209 de dic 30 de 2016
        "aux_transporte": 98200, 
        "uvt": 31859            # Resolución DIAN número 000071 de 2016
    }, 
    2018: {
        "smmlv": 781242,        # Normativa Decreto 2269 de dic 30 de 2017
        "aux_transporte": 104100, 
        "uvt": 33156            # Resolución DIAN número 000063 de 2017
    },
    2019: {
        "smmlv": 828116,        # Normativa Decreto 2451 de dic 27 de 2018
        "aux_transporte": 110400, 
        "uvt": 34270            # Resolución DIAN número 000056 de 2018
    },
    2020: {
        "smmlv": 877803,        # Normativa Decreto 2360 de dic 26 de 2019
        "aux_transporte": 102854, 
        "uvt": 35607            # Resolución DIAN número 000084 de 2019
    },
    2021: {
        "smmlv": 908526,        # Normativa Decreto 1786 de dic 29 de 2020
        "aux_transporte": 106454, 
        "uvt": 36308            # Resolución DIAN número 000111 de 2020
    },
    2022: {
        "smmlv": 1000000,       # Normativa Decreto 1724 de dic 15 de 2021
        "aux_transporte": 117172, 
        "uvt": 38004            # Resolución DIAN número 000140 de 2021
    },
    2023: {
        "smmlv": 1160000,       # Normativa Decreto 2623 de dic 28 2022
        "aux_transporte": 140606, 
        "uvt": 42412            # Resolución DIAN número 001264 de 2022
    },
    2024: {
        "smmlv": 1300000,       # Normativa Decreto 2292 de dic 29 2023
        "aux_transporte": 162000, 
        "uvt": 47065            # Resolución DIAN número 000187 de 2023
    },
    2025: {
        "smmlv": 1423500,       # Normativa Decreto 1572 de dic 24 de 2024
        "aux_transporte": 185000, 
        "uvt": 49799            # Resolución DIAN número 000193 de 2024
    },
    2026: {
        "smmlv": 1750905,       # Normativa Decreto 1469 de dic 29 de 2025 y 0159 de febr. 19 de 2026
        "aux_transporte": 249095, 
        "uvt": 52374            # Resolución DIAN número 000230 de 2025
    }
    # Para años futuros, se recomienda actualizar este diccionario con los nuevos valores oficiales a medida que se publiquen copiando la estructura existente.

}

def obtener_constantes_nomina(fecha_pago: Optional[date] = None) -> Dict[str, Any]:
    """
    Obtiene los valores maestros vigentes para procesar la nómina.
    Garantiza que el diccionario incluya recargos y alertas para la UI.
    """
    if fecha_pago is None:
        fecha_pago = date.today()
        
    año = fecha_pago.year
    
    # Selección de vigencia para el cálculo
    if año not in HISTORICO_LEGAL:
        año_referencia = max(HISTORICO_LEGAL.keys()) if año > 2026 else min(HISTORICO_LEGAL.keys())
        datos = HISTORICO_LEGAL[año_referencia]
    else:
        datos = HISTORICO_LEGAL[año]
        
    # RETORNO INTEGRADO (Asegura que todas las llaves existan)
    return {
        "smmlv": datos["smmlv"],
        "aux_transporte": datos["aux_transporte"],
        "uvt": datos["uvt"],
        "tope_25_smmlv": datos["smmlv"] * 25,
        "año_ejecucion": año,
        "recargos": obtener_tabla_recargos(fecha_pago),  
        "alertas": obtener_alertas_legales(fecha_pago)   
    }

def obtener_divisor_operativo(fecha_pago: date) -> int:
    """
    Determina el divisor operativo de horas según la Ley 2101.
    Afecta directamente el valor de la hora ordinaria para pagos.
    """
    # Punto de corte: 15 de julio de 2026
    FECHA_CAMBIO_LEY = date(2026, 7, 15)
    
    if fecha_pago >= FECHA_CAMBIO_LEY:
        return 210  # Base 42h
    
    return 220      # Base 44h